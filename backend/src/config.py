"""
RepoSense Configuration Management
Handles environment variables and application settings
"""

from typing import Optional
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type conversion.
    """
    
    # WatsonX API Configuration
    watsonx_api_key: str
    watsonx_project_id: str
    
    @field_validator('watsonx_api_key')
    @classmethod
    def validate_api_key(cls, v: str) -> str:
        """Validate that API key is not empty and meets minimum requirements"""
        if not v or len(v.strip()) < 10:
            raise ValueError('watsonx_api_key must be at least 10 characters long')
        if v.strip() in ['your-api-key-here', 'placeholder', 'test', 'dummy']:
            raise ValueError('watsonx_api_key appears to be a placeholder value')
        return v.strip()
    
    @field_validator('watsonx_project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Validate that project ID is not empty"""
        if not v or len(v.strip()) < 5:
            raise ValueError('watsonx_project_id must be at least 5 characters long')
        if v.strip() in ['your-project-id', 'placeholder', 'test']:
            raise ValueError('watsonx_project_id appears to be a placeholder value')
        return v.strip()
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "meta-llama/llama-3-1-70b-instruct"
    
    # API Timeouts (in seconds)
    watsonx_timeout: int = 120
    analysis_timeout: int = 600
    
    # File Processing Limits
    max_file_size_mb: int = 10
    max_files_per_analysis: int = 1000
    
    # Supported Languages
    supported_languages: str = "python,javascript,typescript,java,go,rust"
    
    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Job Management
    job_retention_hours: int = 24
    max_concurrent_jobs: int = 10
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_supported_languages_list(self) -> list[str]:
        """Get supported languages as a list"""
        return [lang.strip() for lang in self.supported_languages.split(",")]
    
    def get_cors_origins_list(self) -> list[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def get_max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024


# Global settings instance
settings = Settings()


# Constants
PROGRESS_STEPS = [
    "Parsing codebase",
    "Analyzing architecture",
    "Reviewing code quality",
    "Generating documentation",
    "Scanning security",
    "Computing health score"
]

# Made with Bob
