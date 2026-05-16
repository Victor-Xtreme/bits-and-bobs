"""
RepoSense Orchestration Logic
Coordinates the entire analysis pipeline
"""

import asyncio
from typing import Optional

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
    try:
        # Stage 0: Parse codebase
        update_job_progress(job_id, 0, StepStatus.active)
        
        try:
            parsed_codebase = await parse_codebase(local_path, job_id)
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.PARSE_FAILED,
                message=f"Failed to parse codebase: {str(e)}",
                stage="Parsing codebase"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 0, StepStatus.done)
        
        # Stage 1: Generate architecture graph
        update_job_progress(job_id, 1, StepStatus.active)
        
        try:
            architecture = await generate_architecture(parsed_codebase)
        except TimeoutError:
            error = AnalysisError(
                code=ErrorCode.AGENT_TIMEOUT,
                message="Architecture generation timed out",
                stage="Analyzing architecture"
            )
            set_job_error(job_id, error)
            return
        except ValueError as e:
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {str(e)}",
                stage="Analyzing architecture"
            )
            set_job_error(job_id, error)
            return
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.WATSONX_UNAVAILABLE,
                message=f"WatsonX API error: {str(e)}",
                stage="Analyzing architecture"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 1, StepStatus.done)
        
        # Stage 2: Generate code review
        update_job_progress(job_id, 2, StepStatus.active)
        
        try:
            review = await generate_review(parsed_codebase)
        except TimeoutError:
            error = AnalysisError(
                code=ErrorCode.AGENT_TIMEOUT,
                message="Code review generation timed out",
                stage="Reviewing code quality"
            )
            set_job_error(job_id, error)
            return
        except ValueError as e:
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {str(e)}",
                stage="Reviewing code quality"
            )
            set_job_error(job_id, error)
            return
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.WATSONX_UNAVAILABLE,
                message=f"WatsonX API error: {str(e)}",
                stage="Reviewing code quality"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 2, StepStatus.done)
        
        # Stage 3: Generate documentation
        update_job_progress(job_id, 3, StepStatus.active)
        
        try:
            docs = await generate_docs(parsed_codebase)
        except TimeoutError:
            error = AnalysisError(
                code=ErrorCode.AGENT_TIMEOUT,
                message="Documentation generation timed out",
                stage="Generating documentation"
            )
            set_job_error(job_id, error)
            return
        except ValueError as e:
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {str(e)}",
                stage="Generating documentation"
            )
            set_job_error(job_id, error)
            return
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.WATSONX_UNAVAILABLE,
                message=f"WatsonX API error: {str(e)}",
                stage="Generating documentation"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 3, StepStatus.done)
        
        # Stage 4: Generate security report
        update_job_progress(job_id, 4, StepStatus.active)
        
        try:
            security = await generate_security(parsed_codebase)
        except TimeoutError:
            error = AnalysisError(
                code=ErrorCode.AGENT_TIMEOUT,
                message="Security scan timed out",
                stage="Scanning security"
            )
            set_job_error(job_id, error)
            return
        except ValueError as e:
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {str(e)}",
                stage="Scanning security"
            )
            set_job_error(job_id, error)
            return
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.WATSONX_UNAVAILABLE,
                message=f"WatsonX API error: {str(e)}",
                stage="Scanning security"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 4, StepStatus.done)
        
        # Stage 5: Compute health score
        update_job_progress(job_id, 5, StepStatus.active)
        
        try:
            score = await generate_score(
                architecture=architecture,
                review=review,
                docs=docs,
                security=security
            )
        except TimeoutError:
            error = AnalysisError(
                code=ErrorCode.AGENT_TIMEOUT,
                message="Health score computation timed out",
                stage="Computing health score"
            )
            set_job_error(job_id, error)
            return
        except ValueError as e:
            error = AnalysisError(
                code=ErrorCode.AGENT_INVALID_JSON,
                message=f"Invalid JSON response: {str(e)}",
                stage="Computing health score"
            )
            set_job_error(job_id, error)
            return
        except Exception as e:
            error = AnalysisError(
                code=ErrorCode.WATSONX_UNAVAILABLE,
                message=f"WatsonX API error: {str(e)}",
                stage="Computing health score"
            )
            set_job_error(job_id, error)
            return
        
        update_job_progress(job_id, 5, StepStatus.done)
        
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
        # Catch-all for unexpected errors
        error = AnalysisError(
            code=ErrorCode.UNKNOWN,
            message=f"Unexpected error: {str(e)}",
            stage="Unknown"
        )
        set_job_error(job_id, error)

# Made with Bob
