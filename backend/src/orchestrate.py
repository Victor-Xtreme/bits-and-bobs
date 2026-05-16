"""
RepoSense Orchestration Logic
Coordinates the entire analysis pipeline
"""

import logging
from typing import Optional, Callable, Any, Awaitable

from .models import (
    AnalysisResult,
    AnalysisError,
    ErrorCode,
    StepStatus
)
from .jobs import (
    update_job_progress,
    set_job_result,
    set_job_error
)
from .parser import parse_codebase
from .watsonx import (
    generate_architecture,
    generate_review,
    generate_docs,
    generate_security,
    generate_score
)

from .config import settings

logger = logging.getLogger(__name__)


async def _run_stage_with_error_handling(
    job_id: str,
    step_index: int,
    stage_name: str,
    stage_func: Callable[..., Awaitable[Any]],
    *args: Any,
    **kwargs: Any
) -> Optional[Any]:
    """
    Execute a stage with standardized error handling.
    
    Args:
        job_id: The job ID for tracking
        step_index: Index of the progress step
        stage_name: Human-readable stage name for error messages
        stage_func: Async function to execute
        *args: Positional arguments for stage_func
        **kwargs: Keyword arguments for stage_func
        
    Returns:
        Result from stage_func, or None if error occurred
        
    Raises:
        Sets job error and returns None on failure
    """
    update_job_progress(job_id, step_index, StepStatus.active)
    
    try:
        result = await stage_func(*args, **kwargs)
        update_job_progress(job_id, step_index, StepStatus.done)
        return result
        
    except TimeoutError as e:
        logger.error(f"{stage_name} timed out: {str(e)}")
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message=f"{stage_name} timed out",
            stage=stage_name
        )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)  # Keep as active to show where it failed
        return None
        
    except ValueError as e:
        # ValueError could be from JSON parsing or other validation issues
        # Check if it's specifically a JSON error by examining the message
        error_msg = str(e)
        if "json" in error_msg.lower() or "parse" in error_msg.lower():
            logger.error(f"{stage_name} invalid JSON: {error_msg}")
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {error_msg}",
                stage=stage_name
            )
        else:
            logger.error(f"{stage_name} validation error: {error_msg}")
            error = AnalysisError(
                code=ErrorCode.UNKNOWN,
                message=f"Validation error: {error_msg}",
                stage=stage_name
            )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)  # Keep as active to show where it failed
        return None
        
    except Exception as e:
        logger.error(f"{stage_name} error: {str(e)}", exc_info=True)
        error = AnalysisError(
            code=ErrorCode.WATSONX_UNAVAILABLE,
            message=f"WatsonX API error: {str(e)}",
            stage=stage_name
        )
        set_job_error(job_id, error)
        update_job_progress(job_id, step_index, StepStatus.active)  # Keep as active to show where it failed
        return None


async def orchestrate_analysis(job_id: str, local_path: str) -> None:
    """
    Main orchestration function that coordinates the entire analysis pipeline.
    
    Pipeline stages:
    1. Parse codebase
    2. Generate architecture graph
    3. Generate code review
    4. Generate documentation
    5. Generate security report
    6. Compute health score
    
    Args:
        job_id: The job ID for tracking progress
        local_path: Path to the local codebase to analyze
    """
    import asyncio
    
    # Apply overall timeout from config
    timeout = settings.analysis_timeout
    
    try:
        # Wrap the entire analysis in a timeout
        await asyncio.wait_for(
            _orchestrate_analysis_impl(job_id, local_path),
            timeout=timeout
        )
    except asyncio.TimeoutError:
        logger.error(f"Analysis timed out after {timeout} seconds")
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message=f"Overall analysis timed out after {timeout} seconds",
            stage="Overall orchestration"
        )
        set_job_error(job_id, error)
    except Exception as e:
        # Catch-all for unexpected errors
        logger.error(f"Unexpected error in orchestration: {str(e)}", exc_info=True)
        error = AnalysisError(
            code=ErrorCode.UNKNOWN,
            message=f"Unexpected error: {str(e)}",
            stage="Unknown"
        )
        set_job_error(job_id, error)


async def _orchestrate_analysis_impl(job_id: str, local_path: str) -> None:
    """
    Internal implementation of the orchestration logic.
    
    Args:
        job_id: The job ID for tracking progress
        local_path: Path to the local codebase to analyze
    """
    try:
        # Stage 0: Parse codebase (special handling for parse errors)
        update_job_progress(job_id, 0, StepStatus.active)
        try:
            parsed_codebase = await parse_codebase(local_path, job_id)
            update_job_progress(job_id, 0, StepStatus.done)
        except Exception as e:
            logger.error(f"Failed to parse codebase: {str(e)}", exc_info=True)
            error = AnalysisError(
                code=ErrorCode.PARSE_FAILED,
                message=f"Failed to parse codebase: {str(e)}",
                stage="Parsing codebase"
            )
            set_job_error(job_id, error)
            return
        
        # Stage 1: Generate architecture graph
        architecture = await _run_stage_with_error_handling(
            job_id, 1, "Analyzing architecture",
            generate_architecture, parsed_codebase
        )
        if architecture is None:
            return
        
        # Stage 2: Generate code review
        review = await _run_stage_with_error_handling(
            job_id, 2, "Reviewing code quality",
            generate_review, parsed_codebase
        )
        if review is None:
            return
        
        # Stage 3: Generate documentation
        docs = await _run_stage_with_error_handling(
            job_id, 3, "Generating documentation",
            generate_docs, parsed_codebase
        )
        if docs is None:
            return
        
        # Stage 4: Generate security report
        security = await _run_stage_with_error_handling(
            job_id, 4, "Scanning security",
            generate_security, parsed_codebase
        )
        if security is None:
            return
        
        # Stage 5: Compute health score
        score = await _run_stage_with_error_handling(
            job_id, 5, "Computing health score",
            generate_score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )
        if score is None:
            return
        
        # Compose final result
        result = AnalysisResult(
            score=score,
            architecture=architecture,
            review=review,
            docs=docs,
            security=security
        )
        
        # Set job result
        set_job_result(job_id, result)
        
    except Exception as e:
        # Re-raise to be caught by outer handler
        raise

# Made with Bob
