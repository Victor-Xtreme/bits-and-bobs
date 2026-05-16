"""
RepoSense FastAPI Application
Main entry point for the codebase analysis API
"""

import asyncio
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware

from .models import (
    AnalyzeRequest,
    ApiResponse,
    PayloadType,
    AnalysisError,
    ErrorCode
)
from .config import settings
from .jobs import (
    create_job,
    get_job,
    cleanup_old_jobs,
    get_active_job_count
)
from .orchestrate import orchestrate_analysis


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
    
    # Start background analysis
    background_tasks.add_task(
        orchestrate_analysis,
        job_id=job_id,
        local_path=request.local_path
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
    if job.status == "completed" and job.result:
        return ApiResponse(
            type=PayloadType.result,
            job_id=job_id,
            progress=job.progress,
            payload=job.result
        )
    elif job.status == "failed" and job.error:
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
    from .jobs import _jobs, _jobs_lock
    
    with _jobs_lock:
        if job_id not in _jobs:
            raise HTTPException(status_code=404, detail="Job not found")
        del _jobs[job_id]
    
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
