"""
Integration tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import sys


@pytest.fixture
def client(mock_env_vars, mock_rag_service, mock_rag_evaluator):
    """Create test client with mocked dependencies."""
    # Import main module and set the global variables before app creation
    import main
    
    # Set the global service instances
    main.rag_service = mock_rag_service
    main.rag_evaluator = mock_rag_evaluator
    
    # Create test client
    return TestClient(main.app)


class TestHealthEndpoints:
    """Test health and stats endpoints."""
    
    def test_root_endpoint(self, client):
        """Test root endpoint."""
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert data["status"] == "healthy"
    
    def test_stats_endpoint(self, client, mock_rag_service):
        """Test stats endpoint."""
        # Ensure mock has proper return value
        mock_rag_service.get_service_stats.return_value = {
            "llm_model": "gpt-3.5-turbo",
            "embedding_model": "text-embedding-ada-002",
            "chunk_size": 1000,
            "chunk_overlap": 200,
            "top_k_results": 5,
            "similarity_threshold": 0.7,
            "conversation_history_length": 0,
            "vector_store_stats": {"document_count": 10}
        }
        
        response = client.get("/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "llm_model" in data
        assert "embedding_model" in data


class TestQuestionEndpoints:
    """Test question answering endpoints."""
    
    def test_ask_question(self, client):
        """Test asking a question."""
        response = client.post(
            "/questions/ask",
            json={
                "question": "What is this about?",
                "k": 5,
                "use_llamaindex": True
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "answer" in data
        assert "sources" in data
    
    def test_ask_question_validation_error(self, client):
        """Test question validation."""
        response = client.post(
            "/questions/ask",
            json={}  # Missing required field
        )
        
        assert response.status_code == 422  # Validation error


class TestConversationEndpoints:
    """Test conversation history endpoints."""
    
    def test_get_conversation_history(self, client):
        """Test getting conversation history."""
        response = client.get("/conversation/history")
        
        assert response.status_code == 200
        assert isinstance(response.json(), list)
    
    def test_clear_conversation_history(self, client):
        """Test clearing conversation history."""
        response = client.delete("/conversation/history")
        
        assert response.status_code == 200
        assert "message" in response.json()

