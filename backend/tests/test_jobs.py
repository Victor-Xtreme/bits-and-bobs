"""
Tests for jobs.py bug fixes
Tests all 5 jobs bugs that were fixed
"""

import pytest
import time
from datetime import datetime, timezone, timedelta
from threading import Thread
from copy import deepcopy

from src.jobs import (
    create_job,
    get_job,
    update_job_progress,
    set_job_result,
    set_job_error,
    cleanup_old_jobs,
    get_active_job_count,
    JobState,
    _jobs
)
from src.models import (
    JobStatus,
    StepStatus,
    AnalysisResult,
    AnalysisError,
    ErrorCode,
    HealthScore
)


class TestTimezoneAwareTimestamps:
    """Test that timestamps are timezone-aware"""
    
    def test_job_created_at_is_timezone_aware(self):
        """Bug fix: created_at should use timezone-aware UTC"""
        job_id = create_job()
        
        # Access internal job state for testing
        from src.jobs import _jobs_lock
        with _jobs_lock:
            job = _jobs.get(job_id)
            assert job is not None
            assert job.created_at.tzinfo is not None
            assert job.created_at.tzinfo == timezone.utc
    
    def test_cleanup_uses_timezone_aware_comparison(self, sample_analysis_result):
        """Bug fix: cleanup_old_jobs should use timezone-aware datetime"""
        # Create a job
        job_id = create_job()
        
        # Mark it as completed (so it can be cleaned up)
        set_job_result(job_id, sample_analysis_result)
        
        # Try cleanup (should not error with timezone comparison)
        removed = cleanup_old_jobs()
        # Job is too new to be removed
        assert removed == 0


class TestRaceConditionFix:
    """Test that race conditions are handled"""
    
    def test_update_progress_handles_deleted_job(self):
        """Bug fix: Should handle job being deleted between lookup and update"""
        job_id = create_job()
        
        # Delete the job from another thread simulation
        with __import__('src.jobs', fromlist=['_jobs_lock'])._jobs_lock:
            if job_id in _jobs:
                del _jobs[job_id]
        
        # This should not crash
        update_job_progress(job_id, 0, StepStatus.active)
    
    def test_concurrent_updates_are_safe(self):
        """Bug fix: Concurrent updates should be thread-safe"""
        job_id = create_job()
        errors = []
        
        def update_worker():
            try:
                for i in range(10):
                    update_job_progress(job_id, 0, StepStatus.active, files_processed=i)
            except Exception as e:
                errors.append(e)
        
        # Run multiple threads
        threads = [Thread(target=update_worker) for _ in range(5)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # Should have no errors
        assert len(errors) == 0


class TestCleanupOnlyCompletedJobs:
    """Test that cleanup doesn't delete running jobs"""
    
    def test_cleanup_skips_running_jobs(self):
        """Bug fix: cleanup_old_jobs should not delete RUNNING jobs"""
        # Create a job
        job_id = create_job()
        
        # Manually set its created_at to be old
        with __import__('src.jobs', fromlist=['_jobs_lock'])._jobs_lock:
            job = _jobs.get(job_id)
            if job:
                # Make it old enough to be cleaned up
                job.created_at = datetime.now(timezone.utc) - timedelta(hours=48)
        
        # Job is still RUNNING, should not be removed
        removed = cleanup_old_jobs()
        
        # Job should still exist
        job_check = get_job(job_id)
        assert job_check is not None
    
    def test_cleanup_removes_completed_old_jobs(self, sample_analysis_result):
        """Test that old completed jobs are removed"""
        # Create a job
        job_id = create_job()
        
        # Mark as completed
        set_job_result(job_id, sample_analysis_result)
        
        # Make it old
        with __import__('src.jobs', fromlist=['_jobs_lock'])._jobs_lock:
            job = _jobs.get(job_id)
            if job:
                job.created_at = datetime.now(timezone.utc) - timedelta(hours=48)
        
        # Should be removed
        removed = cleanup_old_jobs()
        assert removed >= 1


class TestJobErrorHandling:
    """Test job error handling"""
    
    def test_set_job_error_preserves_active_step(self):
        """Bug fix: set_job_error should preserve active step to show where failure occurred"""
        job_id = create_job()
        
        # Set first step as active
        update_job_progress(job_id, 0, StepStatus.active)
        
        # Set error
        error = AnalysisError(
            code=ErrorCode.PARSE_FAILED,
            message="Test error",
            stage="Test stage"
        )
        set_job_error(job_id, error)
        
        # Check job state
        job = get_job(job_id)
        assert job is not None
        assert job.status == JobStatus.FAILED
        assert job.error is not None
        
        # Active step should still be active (showing where it failed)
        assert job.progress[0].status == StepStatus.active


class TestJobLifecycle:
    """Test complete job lifecycle"""
    
    def test_create_and_complete_job(self, sample_analysis_result):
        """Test creating and completing a job"""
        job_id = create_job()
        
        # Job should exist and be running
        job = get_job(job_id)
        assert job is not None
        assert job.status == JobStatus.RUNNING
        assert len(job.progress) > 0
        
        # Complete the job
        set_job_result(job_id, sample_analysis_result)
        
        # Job should be completed
        job = get_job(job_id)
        assert job is not None
        assert job.status == JobStatus.COMPLETED
        assert job.result is not None
    
    def test_get_active_job_count(self, sample_analysis_result):
        """Test counting active jobs"""
        initial_count = get_active_job_count()
        
        # Create some jobs
        job_ids = [create_job() for _ in range(3)]
        
        # Should have 3 more active jobs
        assert get_active_job_count() == initial_count + 3
        
        # Complete one
        set_job_result(job_ids[0], sample_analysis_result)
        
        # Should have 2 active jobs
        assert get_active_job_count() == initial_count + 2


class TestJobProgressUpdates:
    """Test ProgressStep fields update correctly through update_job_progress"""
    
    def test_update_job_progress_updates_files_processed(self):
        """Test that files_processed field updates correctly"""
        job_id = create_job()
        
        # Update with files_processed
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            files_processed=5,
            files_total=10
        )
        
        job = get_job(job_id)
        assert job is not None
        assert job.progress[0].files_processed == 5
        assert job.progress[0].files_total == 10
    
    def test_update_job_progress_updates_current_file(self):
        """Test that current_file field updates correctly"""
        job_id = create_job()
        
        # Update with current_file
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            current_file="src/main.py"
        )
        
        job = get_job(job_id)
        assert job is not None
        assert job.progress[0].current_file == "src/main.py"
    
    def test_update_job_progress_with_all_fields(self):
        """Test updating all progress fields at once"""
        job_id = create_job()
        
        update_job_progress(
            job_id,
            step_index=1,
            status=StepStatus.active,
            files_processed=15,
            files_total=20,
            current_file="src/utils.py"
        )
        
        job = get_job(job_id)
        assert job is not None
        step = job.progress[1]
        assert step.status == StepStatus.active
        assert step.files_processed == 15
        assert step.files_total == 20
        assert step.current_file == "src/utils.py"
    
    def test_progress_step_optional_fields(self):
        """Test that optional fields on ProgressStep work correctly"""
        job_id = create_job()
        
        # Initially, optional fields should be None
        job = get_job(job_id)
        assert job is not None
        assert job.progress[0].files_processed is None
        assert job.progress[0].files_total is None
        assert job.progress[0].current_file is None
        
        # Update only some fields
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            files_processed=3
        )
        
        job = get_job(job_id)
        assert job is not None
        assert job.progress[0].files_processed == 3
        assert job.progress[0].files_total is None  # Still None
        assert job.progress[0].current_file is None  # Still None
    
    def test_update_job_progress_incremental_updates(self):
        """Test that progress can be updated incrementally"""
        job_id = create_job()
        
        # First update
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            files_processed=1,
            files_total=10
        )
        
        # Second update
        update_job_progress(
            job_id,
            step_index=0,
            status=StepStatus.active,
            files_processed=5
        )
        
        job = get_job(job_id)
        assert job is not None
        assert job.progress[0].files_processed == 5
        assert job.progress[0].files_total == 10  # Preserved from first update


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
