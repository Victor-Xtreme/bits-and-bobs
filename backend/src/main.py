"""
RepoSense FastAPI Application
Main entry point for the codebase analysis API
"""

import asyncio
import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .models import (
    AnalyzeRequest,
    ApiResponse,
    PayloadType,
    JobStatus,
    AnalysisError,
    ErrorCode
)
from .config import settings
from . import config as config_module


class ConfigSetupRequest(BaseModel):
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = ""
    watsonx_model_id: str = ""
    orchestrate_api_key: str = ""
    orchestrate_url: str = ""
    orchestrate_instance_id: str = ""
    orchestrate_environment_id: str = ""
    orchestrate_agent_architect_id: str = ""
    orchestrate_agent_reviewer_id: str = ""
    orchestrate_agent_documenter_id: str = ""
    orchestrate_agent_hardener_id: str = ""
from .jobs import (
    create_job,
    get_job,
    cleanup_old_jobs,
    get_active_job_count,
    delete_job as delete_job_from_store
)
from .orchestrate import orchestrate_analysis


def validate_local_path(local_path: str) -> str:
    """
    Validate and sanitize the local path to prevent path traversal attacks.
    
    Args:
        local_path: The path provided by the user
        
    Returns:
        Validated absolute path
        
    Raises:
        HTTPException: If path is invalid or outside allowed directories
    """
    try:
        # Convert to Path object and resolve to absolute path
        path = Path(local_path).resolve()
        
        # Check if path exists
        if not path.exists():
            raise HTTPException(
                status_code=400,
                detail=f"Path does not exist: {local_path}"
            )
        
        # Check if it's a directory
        if not path.is_dir():
            raise HTTPException(
                status_code=400,
                detail=f"Path is not a directory: {local_path}"
            )
        
        # Security check: Prevent access to system directories
        path_str = str(path).lower()
        forbidden_paths = [
            '/etc', '/sys', '/proc', '/dev', '/root',
            'c:\\windows', 'c:\\program files', 'c:\\users\\default'
        ]
        
        for forbidden in forbidden_paths:
            if path_str.startswith(forbidden.lower()):
                raise HTTPException(
                    status_code=403,
                    detail=f"Access to system directories is forbidden"
                )
        
        # Check for path traversal attempts
        if '..' in local_path:
            # Verify the resolved path doesn't escape intended boundaries
            # This is a basic check; in production, you'd want to define
            # specific allowed base directories
            pass
        
        return str(path)
        
    except (OSError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid path: {str(e)}"
        )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: cleanup old jobs
    removed = cleanup_old_jobs()
    print(f"Startup: Cleaned up {removed} old jobs")
    
    yield
    
    # Shutdown: final cleanup
    print("Shutdown: Application closing")


# Initialize FastAPI app
app = FastAPI(
    title="RepoSense API",
    description="AI-powered codebase health analysis tool",
    version="1.0.0",
    lifespan=lifespan
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "service": "RepoSense API",
        "status": "running",
        "version": "1.0.0"
    }


@app.post("/analyze", response_model=ApiResponse)
async def analyze_codebase(
    request: AnalyzeRequest,
    background_tasks: BackgroundTasks
) -> ApiResponse:
    """
    Start a new codebase analysis.
    
    Args:
        request: Analysis request containing local_path
        background_tasks: FastAPI background tasks
        
    Returns:
        ApiResponse with job_id and initial progress
        
    Raises:
        HTTPException: If max concurrent jobs exceeded
    """
    # Validate and sanitize the local path
    validated_path = validate_local_path(request.local_path)
    
    # Check concurrent job limit
    active_jobs = get_active_job_count()
    if active_jobs >= settings.max_concurrent_jobs:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({settings.max_concurrent_jobs}) exceeded"
        )
    
    # Create new job
    job_id = create_job()
    
    # Get initial job state
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=500, detail="Failed to create job")
    
    # Start background analysis with validated path
    background_tasks.add_task(
        orchestrate_analysis,
        job_id=job_id,
        local_path=validated_path
    )
    
    # Return immediate response with job_id and initial progress
    return ApiResponse(
        type=PayloadType.request,
        job_id=job_id,
        progress=job.progress,
        payload=None
    )


@app.get("/jobs/{job_id}", response_model=ApiResponse)
async def get_job_status(job_id: str) -> ApiResponse:
    """
    Get the status and result of an analysis job.
    
    Args:
        job_id: The job ID to query
        
    Returns:
        ApiResponse with current progress and result/error if available
        
    Raises:
        HTTPException: If job not found
    """
    job = get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Determine response type and payload
    if job.status == JobStatus.COMPLETED and job.result:
        return ApiResponse(
            type=PayloadType.result,
            job_id=job_id,
            progress=job.progress,
            payload=job.result
        )
    elif job.status == JobStatus.FAILED and job.error:
        return ApiResponse(
            type=PayloadType.error,
            job_id=job_id,
            progress=job.progress,
            payload=job.error
        )
    else:
        # Still running
        return ApiResponse(
            type=PayloadType.request,
            job_id=job_id,
            progress=job.progress,
            payload=None
        )


@app.delete("/jobs/{job_id}")
async def delete_job(job_id: str):
    """
    Delete a job from the store.
    
    Args:
        job_id: The job ID to delete
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If job not found
    """
    if not delete_job_from_store(job_id):
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {"message": "Job deleted successfully"}


@app.post("/cleanup")
async def trigger_cleanup():
    """
    Manually trigger cleanup of old jobs.

    Returns:
        Number of jobs removed
    """
    removed = cleanup_old_jobs()
    return {"removed": removed}


@app.get("/config/status")
async def config_status():
    """Return whether all required credentials are configured."""
    missing = config_module.settings.missing_fields()
    return {
        "configured": config_module.settings.is_configured(),
        "missing_fields": missing
    }


@app.get("/config/validate")
async def config_validate():
    """
    Test whether the stored credentials actually work by doing a real
    IAM token exchange. Slower than /config/status but catches bad keys.
    """
    if not config_module.settings.is_configured():
        missing = config_module.settings.missing_fields()
        return {"valid": False, "error": f"Missing fields: {', '.join(missing)}"}

    valid, error = await config_module.settings.validate_credentials()
    return {"valid": valid, "error": error}


@app.post("/config/setup")
async def config_setup(body: ConfigSetupRequest):
    """
    Persist credentials to .env and reload settings in memory.
    Only non-empty values are written; existing keys are preserved.
    """
    field_to_env = {
        "watsonx_api_key":                 "WATSONX_API_KEY",
        "watsonx_project_id":              "WATSONX_PROJECT_ID",
        "watsonx_url":                     "WATSONX_URL",
        "watsonx_model_id":                "WATSONX_MODEL_ID",
        "orchestrate_api_key":             "ORCHESTRATE_API_KEY",
        "orchestrate_url":                 "ORCHESTRATE_URL",
        "orchestrate_instance_id":         "ORCHESTRATE_INSTANCE_ID",
        "orchestrate_environment_id":      "ORCHESTRATE_ENVIRONMENT_ID",
        "orchestrate_agent_architect_id":  "ORCHESTRATE_AGENT_ARCHITECT_ID",
        "orchestrate_agent_reviewer_id":   "ORCHESTRATE_AGENT_REVIEWER_ID",
        "orchestrate_agent_documenter_id": "ORCHESTRATE_AGENT_DOCUMENTER_ID",
        "orchestrate_agent_hardener_id":   "ORCHESTRATE_AGENT_HARDENER_ID",
    }

    incoming = body.model_dump()

    env_path = Path(__file__).parent.parent / ".env"
    existing: dict[str, str] = {}
    if env_path.exists():
        for raw_line in env_path.read_text(encoding="utf-8").splitlines():
            line = raw_line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            existing[k.strip().upper()] = v.strip()

    for field, env_var in field_to_env.items():
        value = incoming.get(field, "")
        if isinstance(value, str) and value.strip():
            existing[env_var] = value.strip()
            os.environ[env_var] = value.strip()

    env_path.write_text(
        "\n".join(f"{k}={v}" for k, v in existing.items()) + "\n",
        encoding="utf-8"
    )

    new_settings = config_module.Settings()
    for k, v in new_settings.model_dump().items():
        setattr(config_module.settings, k, v)

    missing = config_module.settings.missing_fields()
    return {
        "configured": config_module.settings.is_configured(),
        "missing_fields": missing
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
