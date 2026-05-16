"""
Pytest configuration and fixtures for RepoSense tests
"""

import os
import pytest

# Set environment variables at module level before any imports
os.environ["WATSONX_API_KEY"] = "test-api-key-1234567890"
os.environ["WATSONX_PROJECT_ID"] = "test-project-id-12345"


@pytest.fixture(scope="session", autouse=True)
def setup_test_environment():
    """Ensure test environment variables are set"""
    # Environment variables are already set at module level
    yield
    
    # Cleanup after tests
    if "WATSONX_API_KEY" in os.environ:
        del os.environ["WATSONX_API_KEY"]
    if "WATSONX_PROJECT_ID" in os.environ:
        del os.environ["WATSONX_PROJECT_ID"]


@pytest.fixture
def sample_analysis_result():
    """Create a sample AnalysisResult for testing"""
    from src.models import (
        AnalysisResult,
        HealthScore,
        Grade,
        ScoreBreakdown,
        ArchitectureGraph,
        CodeReview,
        Documentation,
        SecurityReport
    )
    
    return AnalysisResult(
        score=HealthScore(
            score=85,
            grade=Grade.B,
            breakdown=ScoreBreakdown(
                quality=80,
                security=85,
                documentation=90,
                architecture=85
            ),
            summary="Good overall health",
            top_priorities=["Improve test coverage", "Update dependencies"]
        ),
        architecture=ArchitectureGraph(nodes=[], edges=[]),
        review=CodeReview(findings=[]),
        docs=Documentation(docs=[], tests=[]),
        security=SecurityReport(security=[], modernization=[])
    )

# Made with Bob
