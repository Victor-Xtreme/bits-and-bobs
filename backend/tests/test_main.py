"""
Tests for main.py endpoints
Tests /analyze endpoint, 429 rate limiting, and path traversal protection
"""

import sys
import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient

from src.main import app, validate_local_path
from src.models import PayloadType, AnalysisResult, HealthScore, Grade, ScoreBreakdown
from src.models import ArchitectureGraph, CodeReview, Documentation, SecurityReport


@pytest.fixture
def client():
    """Create a test client"""
    with TestClient(app) as c:
        yield c


class TestAnalyzeEndpoint:
    """Test /analyze endpoint"""
    
    def test_analyze_returns_correct_api_response_shape(self, client, tmp_path):
        """Test that /analyze returns correct ApiResponse shape"""
        test_dir = tmp_path / "test_repo"
        test_dir.mkdir()
        (test_dir / "test.py").write_text("# test")
        
        with patch('src.main.get_active_job_count', return_value=0):
            with patch('src.main.create_job', return_value="test-job-123"):
                with patch('src.main.get_job') as mock_get_job:
                    # Mock job state
                    from src.jobs import JobState
                    mock_job = JobState("test-job-123")
                    mock_get_job.return_value = mock_job
                    
                    response = client.post(
                        "/analyze",
                        json={"local_path": str(test_dir)}
                    )
        
        assert response.status_code == 200
        data = response.json()
        
        # Check ApiResponse structure
        assert "type" in data
        assert "job_id" in data
        assert "progress" in data
        assert "payload" in data
        
        # Should be request type initially
        assert data["type"] == "request"
        assert data["job_id"] == "test-job-123"
        assert isinstance(data["progress"], list)
    
    def test_analyze_validates_path(self, client):
        """Test that /analyze validates the path"""
        response = client.post(
            "/analyze",
            json={"local_path": "/nonexistent/path"}
        )
        
        assert response.status_code == 400
        assert "does not exist" in response.json()["detail"]


class TestRateLimiting:
    """Test 429 rate limiting when max_concurrent_jobs exceeded"""
    
    def test_returns_429_when_max_concurrent_jobs_exceeded(self, client, tmp_path):
        """Test that 429 is returned when max concurrent jobs exceeded"""
        test_dir = tmp_path / "test_repo"
        test_dir.mkdir()
        (test_dir / "test.py").write_text("# test")
        
        with patch('src.main.settings') as mock_settings:
            mock_settings.max_concurrent_jobs = 2
            
            with patch('src.main.get_active_job_count', return_value=2):
                response = client.post(
                    "/analyze",
                    json={"local_path": str(test_dir)}
                )
        
        assert response.status_code == 429
        assert "Maximum concurrent jobs" in response.json()["detail"]
    
    def test_allows_request_when_under_limit(self, client, tmp_path):
        """Test that request is allowed when under the limit"""
        test_dir = tmp_path / "test_repo"
        test_dir.mkdir()
        (test_dir / "test.py").write_text("# test")
        
        with patch('src.main.settings') as mock_settings:
            mock_settings.max_concurrent_jobs = 10
            
            with patch('src.main.get_active_job_count', return_value=5):
                with patch('src.main.create_job', return_value="test-job"):
                    with patch('src.main.get_job') as mock_get_job:
                        from src.jobs import JobState
                        mock_job = JobState("test-job")
                        mock_get_job.return_value = mock_job
                        
                        response = client.post(
                            "/analyze",
                            json={"local_path": str(test_dir)}
                        )
        
        assert response.status_code == 200


class TestPathTraversalProtection:
    """Test path traversal protection in validate_local_path"""
    
    def test_rejects_nonexistent_path(self):
        """Test that nonexistent paths are rejected"""
        from fastapi import HTTPException
        
        with pytest.raises(HTTPException) as exc_info:
            validate_local_path("/nonexistent/path/to/nowhere")
        
        assert exc_info.value.status_code == 400
        assert "does not exist" in exc_info.value.detail
    
    def test_rejects_file_instead_of_directory(self, tmp_path):
        """Test that files are rejected (must be directory)"""
        from fastapi import HTTPException
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")
        
        with pytest.raises(HTTPException) as exc_info:
            validate_local_path(str(test_file))
        
        assert exc_info.value.status_code == 400
        assert "not a directory" in exc_info.value.detail
    
    def test_rejects_system_directories_windows(self):
        """Test that Windows system directories are rejected"""
        from fastapi import HTTPException
        
        # Mock Path.exists and Path.is_dir to return True
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    validate_local_path("C:\\Windows\\System32")
        
        assert exc_info.value.status_code == 403
        assert "forbidden" in exc_info.value.detail.lower()
    
    @pytest.mark.skipif(sys.platform == "win32", reason="Unix-specific test")
    def test_rejects_system_directories_unix(self):
        """Test that Unix system directories are rejected"""
        from fastapi import HTTPException
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.is_dir', return_value=True):
                with pytest.raises(HTTPException) as exc_info:
                    validate_local_path("/etc/passwd")
        
        assert exc_info.value.status_code == 403
        assert "forbidden" in exc_info.value.detail.lower()
    
    def test_accepts_valid_user_directory(self, tmp_path):
        """Test that valid user directories are accepted"""
        test_dir = tmp_path / "my_project"
        test_dir.mkdir()
        
        # Should not raise
        result = validate_local_path(str(test_dir))
        assert result is not None
    
    def test_handles_path_traversal_attempts(self, tmp_path):
        """Test handling of path traversal attempts with .."""
        test_dir = tmp_path / "project"
        test_dir.mkdir()
        
        # Path with .. should still resolve correctly
        path_with_dots = str(test_dir / ".." / test_dir.name)
        
        # Should not raise if it resolves to a valid path
        result = validate_local_path(path_with_dots)
        assert result is not None


class TestGetJobStatusEndpoint:
    """Test /jobs/{job_id} endpoint"""
    
    def test_get_job_status_returns_api_response(self, client):
        """Test that /jobs/{job_id} returns ApiResponse"""
        with patch('src.main.get_job') as mock_get_job:
            from src.jobs import JobState
            from src.models import JobStatus
            
            mock_job = JobState("test-job")
            mock_job.status = JobStatus.RUNNING
            mock_get_job.return_value = mock_job
            
            response = client.get("/jobs/test-job")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "type" in data
        assert "job_id" in data
        assert "progress" in data
        assert data["job_id"] == "test-job"
    
    def test_get_job_status_returns_404_for_missing_job(self, client):
        """Test that 404 is returned for missing job"""
        with patch('src.main.get_job', return_value=None):
            response = client.get("/jobs/nonexistent-job")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob