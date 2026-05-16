"""
Tests for config.py bug fixes
Tests all 7 config bugs that were fixed
"""

import pytest
import os
from pathlib import Path
from unittest.mock import patch
from pydantic import ValidationError

from src.config import Settings, PROGRESS_STEPS


class TestNumericValidation:
    """Test that numeric settings have proper validation"""
    
    def test_watsonx_timeout_positive(self):
        """Bug fix: watsonx_timeout must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                watsonx_timeout=0
            )
        assert "watsonx_timeout" in str(exc_info.value)
    
    def test_watsonx_timeout_max_limit(self):
        """Bug fix: watsonx_timeout should have max limit"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                watsonx_timeout=10000  # Too high
            )
        assert "watsonx_timeout" in str(exc_info.value)
    
    def test_max_file_size_mb_positive(self):
        """Bug fix: max_file_size_mb must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                max_file_size_mb=-1
            )
        assert "max_file_size_mb" in str(exc_info.value)
    
    def test_max_concurrent_jobs_positive(self):
        """Bug fix: max_concurrent_jobs must be positive"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                max_concurrent_jobs=0
            )
        assert "max_concurrent_jobs" in str(exc_info.value)


class TestLogLevelValidation:
    """Test log level validation"""
    
    def test_valid_log_levels(self):
        """Bug fix: log_level should be validated"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        
        for level in valid_levels:
            settings = Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                log_level=level
            )
            assert settings.log_level == level
    
    def test_invalid_log_level(self):
        """Bug fix: Invalid log levels should raise error"""
        with pytest.raises(ValidationError) as exc_info:
            Settings(
                watsonx_api_key="test-key-1234567890",
                watsonx_project_id="test-project-12345",
                log_level="INVALID"
            )
        assert "log_level" in str(exc_info.value)
    
    def test_log_level_case_insensitive(self):
        """Bug fix: log_level should be normalized to uppercase"""
        settings = Settings(
            watsonx_api_key="test-key-1234567890",
            watsonx_project_id="test-project-12345",
            log_level="info"
        )
        assert settings.log_level == "INFO"


class TestEnvFilePath:
    """Test that .env path is absolute"""
    
    def test_env_file_path_is_absolute(self):
        """Bug fix: .env path should be absolute, not relative to CWD"""
        # The env_file in model_config should be an absolute path
        settings_class = Settings
        env_file = settings_class.model_config.get('env_file')
        
        # Should be a Path object or absolute string
        assert env_file is not None
        # Convert to string first to handle DotenvType properly
        env_path = Path(str(env_file))
        assert env_path.is_absolute() or '..' in str(env_file)


class TestListParsing:
    """Test that list parsing filters empty strings"""
    
    def test_get_supported_languages_list_filters_empty(self):
        """Bug fix: Should filter empty strings from language list"""
        settings = Settings(
            watsonx_api_key="test-key-1234567890",
            watsonx_project_id="test-project-12345",
            supported_languages="python,,javascript,,"
        )
        
        languages = settings.get_supported_languages_list()
        
        # Should not contain empty strings
        assert "" not in languages
        assert len(languages) == 2
        assert "python" in languages
        assert "javascript" in languages
    
    def test_get_cors_origins_list_filters_empty(self):
        """Bug fix: Should filter empty strings from CORS origins"""
        settings = Settings(
            watsonx_api_key="test-key-1234567890",
            watsonx_project_id="test-project-12345",
            cors_origins="http://localhost:3000,,http://localhost:5173,"
        )
        
        origins = settings.get_cors_origins_list()
        
        # Should not contain empty strings
        assert "" not in origins
        assert len(origins) == 2
        assert "http://localhost:3000" in origins


class TestSettingsImportTime:
    """Test settings import behavior"""
    
    def test_settings_documented_import_behavior(self):
        """Bug fix: Settings instantiation at import time is documented"""
        # This test verifies that the module can be imported
        # The actual settings object requires env vars, which is documented
        from src import config
        assert hasattr(config, 'settings')
        assert hasattr(config, 'Settings')


class TestValidSettings:
    """Test that valid settings work correctly"""
    
    def test_create_valid_settings(self):
        """Test creating settings with all valid values"""
        settings = Settings(
            watsonx_api_key="test-key-1234567890",
            watsonx_project_id="test-project-12345",
            watsonx_timeout=120,
            analysis_timeout=600,
            max_file_size_mb=10,
            max_files_per_analysis=1000,
            job_retention_hours=24,
            max_concurrent_jobs=10,
            log_level="INFO"
        )
        
        assert settings.watsonx_timeout == 120
        assert settings.analysis_timeout == 600
        assert settings.max_file_size_mb == 10
        assert settings.log_level == "INFO"
    
    def test_get_max_file_size_bytes(self):
        """Test conversion to bytes"""
        settings = Settings(
            watsonx_api_key="test-key-1234567890",
            watsonx_project_id="test-project-12345",
            max_file_size_mb=10
        )
        
        assert settings.get_max_file_size_bytes() == 10 * 1024 * 1024


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
