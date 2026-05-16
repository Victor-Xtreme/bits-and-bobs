"""
Tests for models.py
Tests ApiResponse envelope structure and Union payload type discrimination
"""

import pytest
from pydantic import ValidationError

from src.models import (
    ApiResponse,
    PayloadType,
    AnalysisResult,
    AnalysisError,
    ErrorCode,
    ProgressStep,
    StepStatus,
    HealthScore,
    Grade,
    ScoreBreakdown,
    ArchitectureGraph,
    CodeReview,
    Documentation,
    SecurityReport
)


class TestApiResponseEnvelope:
    """Test ApiResponse envelope structure"""
    
    def test_api_response_with_no_payload(self):
        """Test ApiResponse with request type and no payload"""
        progress = [
            ProgressStep(name="Step 1", status=StepStatus.active),
            ProgressStep(name="Step 2", status=StepStatus.pending)
        ]
        
        response = ApiResponse(
            type=PayloadType.request,
            job_id="test-job-123",
            progress=progress,
            payload=None
        )
        
        assert response.type == PayloadType.request
        assert response.job_id == "test-job-123"
        assert len(response.progress) == 2
        assert response.payload is None
    
    def test_api_response_with_result_payload(self):
        """Test ApiResponse with result type and AnalysisResult payload"""
        progress = [ProgressStep(name="Done", status=StepStatus.done)]
        
        result = AnalysisResult(
            score=HealthScore(
                score=85,
                grade=Grade.B,
                breakdown=ScoreBreakdown(
                    quality=80,
                    security=90,
                    documentation=85,
                    architecture=85
                ),
                summary="Good overall health",
                top_priorities=["Improve documentation"]
            ),
            architecture=ArchitectureGraph(nodes=[], edges=[]),
            review=CodeReview(findings=[]),
            docs=Documentation(docs=[], tests=[]),
            security=SecurityReport(security=[], modernization=[])
        )
        
        response = ApiResponse(
            type=PayloadType.result,
            job_id="test-job-456",
            progress=progress,
            payload=result
        )
        
        assert response.type == PayloadType.result
        assert response.payload is not None
        assert isinstance(response.payload, AnalysisResult)
        assert response.payload.score.score == 85
    
    def test_api_response_with_error_payload(self):
        """Test ApiResponse with error type and AnalysisError payload"""
        progress = [ProgressStep(name="Failed", status=StepStatus.active)]
        
        error = AnalysisError(
            code=ErrorCode.PARSE_FAILED,
            message="Failed to parse file",
            stage="Parsing codebase"
        )
        
        response = ApiResponse(
            type=PayloadType.error,
            job_id="test-job-789",
            progress=progress,
            payload=error
        )
        
        assert response.type == PayloadType.error
        assert response.payload is not None
        assert isinstance(response.payload, AnalysisError)
        assert response.payload.code == ErrorCode.PARSE_FAILED


class TestUnionPayloadTypeDiscrimination:
    """Test Union payload type discrimination"""
    
    def test_payload_can_be_analysis_result(self):
        """Test that payload correctly accepts AnalysisResult"""
        result = AnalysisResult(
            score=HealthScore(
                score=90,
                grade=Grade.A,
                breakdown=ScoreBreakdown(
                    quality=90,
                    security=95,
                    documentation=85,
                    architecture=90
                ),
                summary="Excellent health",
                top_priorities=[]
            ),
            architecture=ArchitectureGraph(nodes=[], edges=[]),
            review=CodeReview(findings=[]),
            docs=Documentation(docs=[], tests=[]),
            security=SecurityReport(security=[], modernization=[])
        )
        
        response = ApiResponse(
            type=PayloadType.result,
            job_id="test",
            progress=[],
            payload=result
        )
        
        # Should be able to access AnalysisResult fields
        assert hasattr(response.payload, 'score')
        assert hasattr(response.payload, 'architecture')
    
    def test_payload_can_be_analysis_error(self):
        """Test that payload correctly accepts AnalysisError"""
        error = AnalysisError(
            code=ErrorCode.AGENT_TIMEOUT,
            message="Analysis timed out",
            stage="Analyzing architecture"
        )
        
        response = ApiResponse(
            type=PayloadType.error,
            job_id="test",
            progress=[],
            payload=error
        )
        
        # Should be able to access AnalysisError fields
        assert hasattr(response.payload, 'code')
        assert hasattr(response.payload, 'message')
        assert hasattr(response.payload, 'stage')
    
    def test_payload_can_be_none(self):
        """Test that payload can be None for request type"""
        response = ApiResponse(
            type=PayloadType.request,
            job_id="test",
            progress=[],
            payload=None
        )
        
        assert response.payload is None
    
    def test_discriminate_result_from_error_by_type(self):
        """Test discriminating between result and error using type field"""
        result_response = ApiResponse(
            type=PayloadType.result,
            job_id="test1",
            progress=[],
            payload=AnalysisResult(
                score=HealthScore(
                    score=75,
                    grade=Grade.C,
                    breakdown=ScoreBreakdown(
                        quality=70,
                        security=80,
                        documentation=75,
                        architecture=75
                    ),
                    summary="Needs improvement",
                    top_priorities=["Fix security issues"]
                ),
                architecture=ArchitectureGraph(nodes=[], edges=[]),
                review=CodeReview(findings=[]),
                docs=Documentation(docs=[], tests=[]),
                security=SecurityReport(security=[], modernization=[])
            )
        )
        
        error_response = ApiResponse(
            type=PayloadType.error,
            job_id="test2",
            progress=[],
            payload=AnalysisError(
                code=ErrorCode.UNKNOWN,
                message="Unknown error",
                stage="Unknown"
            )
        )
        
        # Can discriminate by checking the type field
        assert result_response.type == PayloadType.result
        assert error_response.type == PayloadType.error
        
        # Can also check payload type
        assert isinstance(result_response.payload, AnalysisResult)
        assert isinstance(error_response.payload, AnalysisError)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob