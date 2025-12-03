"""
Unit tests for HealthController.
"""
import pytest
from fastapi import HTTPException

from src.controllers.health_controller import HealthController


class TestHealthController:
    """Test HealthController class."""
    
    @pytest.fixture
    def controller(self, mock_rag_service):
        """Create HealthController instance."""
        return HealthController(mock_rag_service)
    
    @pytest.mark.asyncio
    async def test_health_check_success(self, controller):
        """Test successful health check."""
        result = await controller.health_check()
        
        assert result.status == "healthy"
        assert result.timestamp is not None
    
    @pytest.mark.asyncio
    async def test_root_endpoint(self, controller):
        """Test root endpoint."""
        result = await controller.root()
        
        assert result.status == "healthy"
        assert result.version is not None
    
    @pytest.mark.asyncio
    async def test_get_stats_success(self, controller, mock_rag_service):
        """Test getting service stats."""
        result = await controller.get_stats()
        
        assert result.llm_model == "gpt-3.5-turbo"
        assert result.embedding_model == "text-embedding-ada-002"
        assert mock_rag_service.get_service_stats.called
    
    @pytest.mark.asyncio
    async def test_get_stats_no_service(self):
        """Test stats when service not initialized."""
        controller = HealthController(None)
        
        with pytest.raises(HTTPException) as exc:
            await controller.get_stats()
        
        assert exc.value.status_code == 503

