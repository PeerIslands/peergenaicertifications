"""
Unit tests for Pydantic schemas.
"""
import pytest
from pydantic import ValidationError

from src.models.schemas import (
    QuestionRequest,
    QuestionResponse,
    DocumentUploadRequest,
    DocumentUploadResponse,
    HealthCheckResponse,
    EvaluationMetrics
)


class TestSchemas:
    """Test Pydantic schema models."""
    
    def test_question_request_valid(self):
        """Test valid QuestionRequest."""
        request = QuestionRequest(
            question="What is this?",
            k=5,
            use_conversation_history=False
        )
        
        assert request.question == "What is this?"
        assert request.k == 5
        assert request.use_conversation_history is False
    
    def test_question_request_defaults(self):
        """Test QuestionRequest defaults."""
        request = QuestionRequest(question="Test")
        
        assert request.k == 5  # Default value
        assert request.use_conversation_history is False
    
    def test_question_response_valid(self):
        """Test valid QuestionResponse."""
        response = QuestionResponse(
            answer="Test answer",
            sources=[],
            num_sources=0,
            processing_time=0.5,
            timestamp="2024-12-01T10:00:00"
        )
        
        assert response.answer == "Test answer"
        assert response.num_sources == 0
    
    def test_document_upload_request(self):
        """Test DocumentUploadRequest."""
        request = DocumentUploadRequest(file_path="/path/to/file.pdf")
        
        assert request.file_path == "/path/to/file.pdf"
        assert request.directory_path is None
    
    def test_health_check_response(self):
        """Test HealthCheckResponse."""
        response = HealthCheckResponse(
            status="healthy",
            timestamp="2024-12-01T10:00:00"
        )
        
        assert response.status == "healthy"
        assert response.version == "1.0.0"  # Default
    
    def test_evaluation_metrics(self):
        """Test EvaluationMetrics."""
        metrics = EvaluationMetrics(
            answer_relevance=0.85,
            context_relevance=0.80,
            groundedness=0.90,
            overall_quality=0.85
        )
        
        assert metrics.answer_relevance == 0.85
        assert metrics.overall_quality == 0.85

