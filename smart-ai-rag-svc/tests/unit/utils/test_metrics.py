"""
Unit tests for metrics module.
Tests Prometheus metrics tracking and cost calculations.
"""
import pytest
from unittest.mock import patch, MagicMock
from prometheus_client import REGISTRY

from src.utils.metrics import (
    track_document_processed,
    track_question_answered,
    track_llm_cost,
    track_operation_duration,
    track_evaluation,
    track_error,
    OPENAI_PRICING,
    documents_processed_total,
    questions_answered_total,
    openai_cost_dollars_total,
    llm_tokens_used_total,
    errors_total,
    evaluations_total
)


class TestMetricsTracking:
    """Test metrics tracking functions."""
    
    def test_track_document_processed_success(self):
        """Test tracking successful document processing."""
        # Get initial value
        initial_value = documents_processed_total.labels(
            framework="llamaindex",
            status="success"
        )._value.get()
        
        # Track document processing
        track_document_processed(framework="llamaindex", status="success", chunks=42)
        
        # Verify metric increased
        new_value = documents_processed_total.labels(
            framework="llamaindex",
            status="success"
        )._value.get()
        
        assert new_value == initial_value + 1
        
    def test_track_document_processed_error(self):
        """Test tracking failed document processing."""
        initial_value = documents_processed_total.labels(
            framework="langchain",
            status="error"
        )._value.get()
        
        track_document_processed(framework="langchain", status="error")
        
        new_value = documents_processed_total.labels(
            framework="langchain",
            status="error"
        )._value.get()
        
        assert new_value == initial_value + 1
        
    def test_track_question_answered_success(self):
        """Test tracking successful question answering."""
        initial_value = questions_answered_total.labels(
            framework="llamaindex",
            status="success"
        )._value.get()
        
        track_question_answered(framework="llamaindex", status="success")
        
        new_value = questions_answered_total.labels(
            framework="llamaindex",
            status="success"
        )._value.get()
        
        assert new_value == initial_value + 1
        
    def test_track_question_answered_error(self):
        """Test tracking failed question answering."""
        initial_value = questions_answered_total.labels(
            framework="langchain",
            status="error"
        )._value.get()
        
        track_question_answered(framework="langchain", status="error")
        
        new_value = questions_answered_total.labels(
            framework="langchain",
            status="error"
        )._value.get()
        
        assert new_value == initial_value + 1


class TestCostTracking:
    """Test OpenAI cost tracking."""
    
    def test_openai_pricing_data(self):
        """Test that pricing data is available for common models."""
        assert "gpt-3.5-turbo" in OPENAI_PRICING
        assert "gpt-4" in OPENAI_PRICING
        assert "text-embedding-ada-002" in OPENAI_PRICING
        
        # Check pricing structure
        assert "prompt" in OPENAI_PRICING["gpt-3.5-turbo"]
        assert "completion" in OPENAI_PRICING["gpt-3.5-turbo"]
        
    def test_track_llm_cost_gpt35(self):
        """Test tracking cost for GPT-3.5-turbo."""
        initial_cost = openai_cost_dollars_total.labels(
            model="gpt-3.5-turbo",
            operation="generation"
        )._value.get()
        
        # Track usage: 100 prompt tokens, 50 completion tokens
        track_llm_cost(
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            operation="generation"
        )
        
        new_cost = openai_cost_dollars_total.labels(
            model="gpt-3.5-turbo",
            operation="generation"
        )._value.get()
        
        # Calculate expected cost
        expected_cost = (100 * 0.0005 / 1000) + (50 * 0.0015 / 1000)
        
        assert new_cost == pytest.approx(initial_cost + expected_cost, rel=1e-6)
        
    def test_track_llm_cost_gpt4(self):
        """Test tracking cost for GPT-4."""
        initial_cost = openai_cost_dollars_total.labels(
            model="gpt-4",
            operation="generation"
        )._value.get()
        
        track_llm_cost(
            model="gpt-4",
            prompt_tokens=100,
            completion_tokens=50,
            operation="generation"
        )
        
        new_cost = openai_cost_dollars_total.labels(
            model="gpt-4",
            operation="generation"
        )._value.get()
        
        # GPT-4 is more expensive
        expected_cost = (100 * 0.03 / 1000) + (50 * 0.06 / 1000)
        
        assert new_cost == pytest.approx(initial_cost + expected_cost, rel=1e-6)
        
    def test_track_llm_cost_embeddings(self):
        """Test tracking cost for embeddings."""
        initial_cost = openai_cost_dollars_total.labels(
            model="text-embedding-ada-002",
            operation="embedding"
        )._value.get()
        
        track_llm_cost(
            model="text-embedding-ada-002",
            prompt_tokens=1000,
            completion_tokens=0,
            operation="embedding"
        )
        
        new_cost = openai_cost_dollars_total.labels(
            model="text-embedding-ada-002",
            operation="embedding"
        )._value.get()
        
        expected_cost = 1000 * 0.0001 / 1000
        
        assert new_cost == pytest.approx(initial_cost + expected_cost, rel=1e-6)
        
    def test_track_llm_tokens(self):
        """Test that token usage is tracked separately."""
        initial_prompt = llm_tokens_used_total.labels(
            provider="openai",
            model="gpt-3.5-turbo",
            type="prompt"
        )._value.get()
        
        initial_completion = llm_tokens_used_total.labels(
            provider="openai",
            model="gpt-3.5-turbo",
            type="completion"
        )._value.get()
        
        track_llm_cost(
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            operation="generation"
        )
        
        new_prompt = llm_tokens_used_total.labels(
            provider="openai",
            model="gpt-3.5-turbo",
            type="prompt"
        )._value.get()
        
        new_completion = llm_tokens_used_total.labels(
            provider="openai",
            model="gpt-3.5-turbo",
            type="completion"
        )._value.get()
        
        assert new_prompt == initial_prompt + 100
        assert new_completion == initial_completion + 50


class TestEvaluationTracking:
    """Test evaluation metrics tracking."""
    
    def test_track_evaluation_success(self):
        """Test tracking successful evaluation."""
        initial_value = evaluations_total.labels(status="success")._value.get()
        
        scores = {
            "answer_relevance": 0.95,
            "context_relevance": 0.88,
            "groundedness": 0.92
        }
        
        track_evaluation(scores, status="success")
        
        new_value = evaluations_total.labels(status="success")._value.get()
        assert new_value == initial_value + 1
        
    def test_track_evaluation_with_non_numeric_scores(self):
        """Test tracking evaluation with mixed score types."""
        scores = {
            "answer_relevance": 0.95,
            "quality_level": "excellent",  # String, should be skipped
            "groundedness": 0.92
        }
        
        # Should not raise an error
        track_evaluation(scores, status="success")


class TestErrorTracking:
    """Test error tracking."""
    
    def test_track_error(self):
        """Test tracking errors."""
        initial_value = errors_total.labels(
            type="ValueError",
            component="api"
        )._value.get()
        
        track_error(error_type="ValueError", component="api")
        
        new_value = errors_total.labels(
            type="ValueError",
            component="api"
        )._value.get()
        
        assert new_value == initial_value + 1
        
    def test_track_different_error_types(self):
        """Test tracking different error types."""
        track_error(error_type="TimeoutError", component="llm")
        track_error(error_type="ConnectionError", component="database")
        track_error(error_type="ValidationError", component="api")
        
        # All should be tracked without errors
        assert True


class TestOperationDuration:
    """Test operation duration tracking."""
    
    def test_track_operation_duration_context_manager(self):
        """Test operation duration tracking with context manager."""
        import time
        
        with track_operation_duration("document_processing", {"framework": "llamaindex"}):
            time.sleep(0.01)  # Simulate work
        
        # If no exception is raised, the test passes
        assert True
        
    def test_track_operation_duration_question_answering(self):
        """Test tracking question answering duration."""
        import time
        
        with track_operation_duration("question_answering", {"framework": "langchain"}):
            time.sleep(0.01)
        
        assert True
        
    def test_track_operation_duration_llm_request(self):
        """Test tracking LLM request duration."""
        import time
        
        with track_operation_duration("llm_request", {"provider": "openai", "model": "gpt-3.5-turbo"}):
            time.sleep(0.01)
        
        assert True


class TestMetricsIntegration:
    """Integration tests for metrics."""
    
    def test_complete_document_processing_flow(self):
        """Test complete document processing metrics flow."""
        framework = "llamaindex"
        
        # Track document processing
        with track_operation_duration("document_processing", {"framework": framework}):
            track_document_processed(framework=framework, status="success", chunks=42)
        
        # Verify no exceptions
        assert True
        
    def test_complete_question_answering_flow(self):
        """Test complete question answering metrics flow."""
        framework = "langchain"
        
        # Track question answering
        with track_operation_duration("question_answering", {"framework": framework}):
            track_question_answered(framework=framework, status="success")
            
        # Track LLM cost
        track_llm_cost(
            model="gpt-3.5-turbo",
            prompt_tokens=100,
            completion_tokens=50,
            operation="generation"
        )
        
        assert True
        
    def test_error_flow(self):
        """Test error tracking flow."""
        framework = "llamaindex"
        
        # Simulate error
        track_document_processed(framework=framework, status="error")
        track_error(error_type="ProcessingError", component="document_processor")
        
        assert True
