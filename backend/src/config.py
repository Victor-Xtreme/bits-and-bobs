"""
RepoSense Configuration Management
Handles environment variables and application settings
"""

from pathlib import Path
from typing import List
from pydantic import field_validator, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    Uses pydantic-settings for validation and type conversion.
    """
    
    # WatsonX API Configuration (empty default so backend starts without .env)
    watsonx_api_key: str = ""
    watsonx_project_id: str = ""
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "meta-llama/llama-3-3-70b-instruct"

    # WatsonX Orchestrate Configuration
    orchestrate_api_key: str = ""
    orchestrate_url: str = ""
    orchestrate_timeout: int = Field(default=120, gt=0, le=3600)
    orchestrate_model_id: str = "ibm/granite-8b-code-instruct"
    orchestrate_agent_architect_id: str = ""
    orchestrate_agent_reviewer_id: str = ""
    orchestrate_agent_documenter_id: str = ""
    orchestrate_agent_hardener_id: str = ""
    orchestrate_environment_id: str = ""
    orchestrate_instance_id: str = ""

    # API Timeouts (in seconds)
    watsonx_timeout: int = Field(default=120, gt=0, le=3600)
    analysis_timeout: int = Field(default=600, gt=0, le=7200)
    
    # File Processing Limits
    max_file_size_mb: int = Field(default=10, gt=0, le=1000)
    max_files_per_analysis: int = Field(default=1000, gt=0, le=100000)
    
    # Supported Languages
    supported_languages: str = "py,js,ts,java,go,rs"
    
    # CORS Settings
    cors_origins: str = "http://localhost:3000,http://localhost:5173"
    
    # Job Management
    job_retention_hours: int = Field(default=24, gt=0, le=720)
    max_concurrent_jobs: int = Field(default=10, gt=0, le=100)
    
    # Logging
    log_level: str = "INFO"
    
    @field_validator('log_level')
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate that log level is valid"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f'log_level must be one of {valid_levels}')
        return v_upper
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent.parent / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    def get_supported_languages_list(self) -> List[str]:
        """Get supported languages as a list"""
        return [lang.strip() for lang in self.supported_languages.split(",") if lang.strip()]
    
    def get_cors_origins_list(self) -> List[str]:
        """Get CORS origins as a list"""
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]
    
    def get_max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024

    def missing_fields(self) -> list[str]:
        """Return names of required fields that are not yet set."""
        required = {
            "watsonx_api_key":                  self.watsonx_api_key,
            "watsonx_project_id":               self.watsonx_project_id,
            "orchestrate_api_key":              self.orchestrate_api_key,
            "orchestrate_url":                  self.orchestrate_url,
            "orchestrate_instance_id":          self.orchestrate_instance_id,
            "orchestrate_environment_id":       self.orchestrate_environment_id,
            "orchestrate_agent_architect_id":   self.orchestrate_agent_architect_id,
            "orchestrate_agent_reviewer_id":    self.orchestrate_agent_reviewer_id,
            "orchestrate_agent_documenter_id":  self.orchestrate_agent_documenter_id,
            "orchestrate_agent_hardener_id":    self.orchestrate_agent_hardener_id,
        }
        return [k for k, v in required.items() if not v or not v.strip()]

    def is_configured(self) -> bool:
        return len(self.missing_fields()) == 0


# Global settings instance
# Note: This will fail at import time if required env vars are missing.
# For testing or tooling that needs to import without loading config,
# consider mocking or setting dummy env vars.
settings = Settings()  # type: ignore[call-arg]


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
