"""
RepoSense Job Management System
Thread-safe in-memory job store for tracking analysis progress
"""

import uuid
from datetime import datetime, timedelta, timezone
from threading import Lock
from typing import Optional, Dict, List

from .models import (
    ProgressStep,
    StepStatus,
    JobStatus,
    AnalysisResult,
    AnalysisError,
    ErrorCode,
    ApiResponse,
    PayloadType
)
from .config import settings, PROGRESS_STEPS


# Job state structure
class JobState:
    """Internal job state representation"""
    
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.created_at = datetime.now(timezone.utc)
        self.status = JobStatus.RUNNING
        self.progress: List[ProgressStep] = []
        self.result: Optional[AnalysisResult] = None
        self.error: Optional[AnalysisError] = None
        self._lock = Lock()  # Per-job lock for thread safety
        
        # Initialize progress steps
        for step_name in PROGRESS_STEPS:
            self.progress.append(
                ProgressStep(
                    name=step_name,
                    status=StepStatus.pending
                )
            )
        # Set first step as active
        if self.progress:
            self.progress[0].status = StepStatus.active


# In-memory job store
_jobs: Dict[str, JobState] = {}
_jobs_lock = Lock()


def create_job() -> str:
    """
    Create a new job and return its ID.
    
    Returns:
        str: Unique job ID
    """
    job_id = str(uuid.uuid4())
    
    with _jobs_lock:
        _jobs[job_id] = JobState(job_id)
    
    return job_id


def get_job(job_id: str) -> Optional[JobState]:
    """
    Retrieve a job by ID. Returns a snapshot copy to prevent external mutation.
    
    Args:
        job_id: The job ID to retrieve
        
    Returns:
        Snapshot copy of JobState if found, None otherwise
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if job is None:
            return None
        
        # Create a new JobState with copied data (avoiding lock copy issues)
        job_copy = JobState.__new__(JobState)
        job_copy.job_id = job.job_id
        job_copy.created_at = job.created_at
        job_copy.status = job.status
        job_copy.progress = [
            ProgressStep(
                name=step.name,
                status=step.status,
                files_processed=step.files_processed,
                files_total=step.files_total,
                current_file=step.current_file
            ) for step in job.progress
        ]
        job_copy.result = job.result
        job_copy.error = job.error
        job_copy._lock = Lock()  # New lock for the copy
        
        return job_copy


def update_job_progress(
    job_id: str,
    step_index: int,
    status: StepStatus,
    files_processed: Optional[int] = None,
    files_total: Optional[int] = None,
    current_file: Optional[str] = None
) -> None:
    """
    Update progress for a specific step with improved thread safety.
    
    Args:
        job_id: The job ID
        step_index: Index of the step to update (0-based)
        status: New status for the step
        files_processed: Optional number of files processed
        files_total: Optional total number of files
        current_file: Optional current file being processed
    """
    # Get job reference under global lock and check status
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
        
        # Check if job is still running before updating
        if job.status != JobStatus.RUNNING:
            return
        
        # Keep reference to job while we have the lock
        job_ref = job
    
    # Use per-job lock for finer-grained control
    with job_ref._lock:
        if 0 <= step_index < len(job_ref.progress):
            step = job_ref.progress[step_index]
            step.status = status
            
            if files_processed is not None:
                step.files_processed = files_processed
            if files_total is not None:
                step.files_total = files_total
            if current_file is not None:
                step.current_file = current_file
            
            # If marking as done, set next step as active (only if still running)
            if status == StepStatus.done and step_index + 1 < len(job_ref.progress):
                next_step = job_ref.progress[step_index + 1]
                if next_step.status == StepStatus.pending:
                    next_step.status = StepStatus.active


def set_job_result(job_id: str, result: AnalysisResult) -> None:
    """
    Set the final result for a job and mark it as completed.
    
    Args:
        job_id: The job ID
        result: The analysis result
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
    
    with job._lock:
        job.status = JobStatus.COMPLETED
        job.result = result
        
        # Mark all steps as done
        for step in job.progress:
            step.status = StepStatus.done


def set_job_error(job_id: str, error: AnalysisError) -> None:
    """
    Set an error for a job and mark it as failed.
    
    Args:
        job_id: The job ID
        error: The analysis error
    """
    with _jobs_lock:
        job = _jobs.get(job_id)
        if not job:
            return
        job_ref = job
    
    with job_ref._lock:
        job_ref.status = JobStatus.FAILED
        job_ref.error = error
        
        # Leave active step as-is to show where failure occurred
        # The job status FAILED indicates the overall failure


def cleanup_old_jobs() -> int:
    """
    Remove jobs older than the retention period.
    Only removes completed or failed jobs, not running jobs.
    
    Returns:
        int: Number of jobs removed
    """
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=settings.job_retention_hours)
    removed_count = 0
    
    with _jobs_lock:
        job_ids_to_remove = [
            job_id for job_id, job in _jobs.items()
            if job.created_at < cutoff_time and job.status != JobStatus.RUNNING
        ]
        
        for job_id in job_ids_to_remove:
            del _jobs[job_id]
            removed_count += 1
    
    return removed_count


def get_active_job_count() -> int:
    """
    Get the number of currently running jobs.
    
    Returns:
        int: Number of active jobs
    """
    with _jobs_lock:
        return sum(1 for job in _jobs.values() if job.status == JobStatus.RUNNING)


def delete_job(job_id: str) -> bool:
    """
    Delete a job from the store.
    
    Args:
        job_id: The job ID to delete
        
    Returns:
        bool: True if job was found and deleted, False otherwise
    """
    with _jobs_lock:
        if job_id in _jobs:
            del _jobs[job_id]
            return True
        return False


def get_job_status(job_id: str) -> Optional[ApiResponse]:
    """
    Get job status as API response.
    
    Args:
        job_id: The job ID
        
    Returns:
        ApiResponse if found, None otherwise
    """
    job = get_job(job_id)
    if job is None:
        return None
    
    # Determine payload type and content
    if job.status == JobStatus.COMPLETED and job.result:
        payload_type = PayloadType.result
        payload = job.result
    elif job.status == JobStatus.FAILED and job.error:
        payload_type = PayloadType.error
        payload = job.error
    else:
        payload_type = PayloadType.request
        payload = None
    
    return ApiResponse(
        type=payload_type,
        job_id=job.job_id,
        progress=job.progress,
        payload=payload
    )

# Made with Bob
