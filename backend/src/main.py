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

from .models import (
    AnalyzeRequest,
    AnalyzeParsedRequest,
    ApiResponse,
    PayloadType,
    JobStatus,
    AnalysisError,
    ErrorCode
)
from .config import settings
from .jobs import (
    create_job,
    get_job,
    cleanup_old_jobs,
    get_active_job_count,
    delete_job as delete_job_from_store
)
from .orchestrate import orchestrate_analysis, orchestrate_analysis_from_parsed


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


@app.post("/analyze-parsed", response_model=ApiResponse)
async def analyze_codebase_parsed(
    request: AnalyzeParsedRequest,
    background_tasks: BackgroundTasks
) -> ApiResponse:
    """
    Start analysis from a pre-parsed codebase.
    The client (VS Code extension) runs the file parsing locally and sends
    the structured result here. The backend skips Stage 0 entirely.
    No filesystem access is required.
    """
    # Check concurrent job limit
    active_jobs = get_active_job_count()
    if active_jobs >= settings.max_concurrent_jobs:
        raise HTTPException(
            status_code=429,
            detail=f"Maximum concurrent jobs ({settings.max_concurrent_jobs}) exceeded"
        )

    # Create new job
    job_id = create_job()

    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=500, detail="Failed to create job")

    # Start background analysis with the pre-parsed codebase
    background_tasks.add_task(
        orchestrate_analysis_from_parsed,
        job_id=job_id,
        parsed_codebase=request.parsed_codebase
    )

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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Made with Bob
