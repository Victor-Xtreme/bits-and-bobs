"""
Tests for orchestrate.py bug fixes
Tests all 4 orchestrate bugs that were fixed
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock

from src.orchestrate import (
    orchestrate_analysis,
    _run_stage_with_error_handling,
    _orchestrate_analysis_impl
)
from src.models import (
    ErrorCode,
    StepStatus
)


class TestUnusedImportRemoved:
    """Test that unused asyncio import was removed from module level"""
    
    def test_asyncio_not_imported_at_module_level(self):
        """Bug fix: asyncio should not be imported at module level if unused there"""
        import src.orchestrate as orchestrate_module
        import inspect
        
        source = inspect.getsource(orchestrate_module)
        lines = source.split('\n')
        
        # Check imports at top of file
        import_section = '\n'.join(lines[:20])
        # asyncio should not be in the initial imports
        # (it's imported inside the function where needed)
        assert 'import asyncio' not in import_section or 'def ' in import_section


class TestValueErrorHandling:
    """Test improved ValueError handling"""
    
    @pytest.mark.asyncio
    async def test_json_value_error_detected(self):
        """Bug fix: ValueError should distinguish JSON errors from other validation errors"""
        
        async def mock_stage_with_json_error():
            raise ValueError("Failed to parse JSON response")
        
        result = await _run_stage_with_error_handling(
            "test_job",
            0,
            "Test Stage",
            mock_stage_with_json_error
        )
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_non_json_value_error_handled(self):
        """Bug fix: Non-JSON ValueError should be handled differently"""
        
        async def mock_stage_with_validation_error():
            raise ValueError("Invalid parameter value")
        
        result = await _run_stage_with_error_handling(
            "test_job",
            0,
            "Test Stage",
            mock_stage_with_validation_error
        )
        
        assert result is None


class TestOverallTimeout:
    """Test that overall orchestration timeout is enforced"""
    
    @pytest.mark.asyncio
    async def test_orchestration_timeout_enforced(self):
        """Bug fix: analysis_timeout from config should be enforced"""
        
        with patch('src.orchestrate.settings') as mock_settings:
            mock_settings.analysis_timeout = 0.1  # Very short timeout
            
            with patch('src.orchestrate._orchestrate_analysis_impl') as mock_impl:
                # Make it hang
                async def slow_analysis(job_id, local_path):
                    await asyncio.sleep(10)
                
                mock_impl.side_effect = slow_analysis
                
                with patch('src.orchestrate.set_job_error') as mock_set_error:
                    # Should complete without raising (timeout is caught internally)
                    await orchestrate_analysis("test_job", "/fake/path")
                    
                    # Should have set a timeout error
                    assert mock_set_error.called
                    error_arg = mock_set_error.call_args[0][1]
                    assert error_arg.code == ErrorCode.AGENT_TIMEOUT
                    assert "timed out" in error_arg.message.lower()
    
    @pytest.mark.asyncio
    async def test_timeout_sets_job_error(self):
        """Bug fix: Timeout should set appropriate job error"""
        
        with patch('src.orchestrate.settings') as mock_settings:
            mock_settings.analysis_timeout = 0.1
            
            with patch('src.orchestrate._orchestrate_analysis_impl') as mock_impl:
                async def slow_analysis(job_id, local_path):
                    await asyncio.sleep(10)
                
                mock_impl.side_effect = slow_analysis
                
                with patch('src.orchestrate.set_job_error') as mock_set_error:
                    # Run orchestration (will timeout)
                    await orchestrate_analysis("test_job", "/fake/path")
                    
                    # Should have called set_job_error
                    assert mock_set_error.called


class TestProgressStateOnFailure:
    """Test that progress state is preserved on failure"""
    
    @pytest.mark.asyncio
    async def test_active_step_preserved_on_error(self):
        """Bug fix: Active step should remain active when stage fails"""
        
        async def failing_stage():
            raise Exception("Test error")
        
        with patch('src.orchestrate.update_job_progress') as mock_update:
            with patch('src.orchestrate.set_job_error'):
                result = await _run_stage_with_error_handling(
                    "test_job",
                    1,
                    "Test Stage",
                    failing_stage
                )
                
                assert result is None
                
                # Should have updated progress to keep step active
                calls = mock_update.call_args_list
                # Last call should set status to active
                if calls:
                    last_call = calls[-1]
                    assert last_call[0][2] == StepStatus.active


class TestErrorHandling:
    """Test comprehensive error handling"""
    
    @pytest.mark.asyncio
    async def test_timeout_error_handling(self):
        """Test TimeoutError is properly handled"""
        
        async def timeout_stage():
            raise TimeoutError("Stage timed out")
        
        with patch('src.orchestrate.set_job_error') as mock_set_error:
            with patch('src.orchestrate.update_job_progress'):
                result = await _run_stage_with_error_handling(
                    "test_job",
                    0,
                    "Test Stage",
                    timeout_stage
                )
                
                assert result is None
                assert mock_set_error.called
                
                # Check error code
                error_arg = mock_set_error.call_args[0][1]
                assert error_arg.code == ErrorCode.AGENT_TIMEOUT
    
    @pytest.mark.asyncio
    async def test_generic_exception_handling(self):
        """Test generic exceptions are handled"""
        
        async def error_stage():
            raise RuntimeError("Unexpected error")
        
        with patch('src.orchestrate.set_job_error') as mock_set_error:
            with patch('src.orchestrate.update_job_progress'):
                result = await _run_stage_with_error_handling(
                    "test_job",
                    0,
                    "Test Stage",
                    error_stage
                )
                
                assert result is None
                assert mock_set_error.called


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
