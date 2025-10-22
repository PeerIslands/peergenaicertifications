"""Tests for chat service."""
import pytest
from unittest.mock import Mock, patch, AsyncMock


class TestChatService:
    """Test cases for chat service."""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, mock_openai, mock_mongodb):
        """Test successful message sending."""
        from src.services.chat_service import ChatService
        
        service = ChatService()
        
        # Mock the necessary methods
        with patch.object(service, 'get_session_context', return_value="Test context"):
            response = await service.process_message(
                session_id="test_session_123",
                message="What is this document about?"
            )
            
            assert response is not None
            assert isinstance(response, str)
    
    @pytest.mark.asyncio
    async def test_send_message_empty(self):
        """Test sending empty message."""
        from src.services.chat_service import ChatService
        
        service = ChatService()
        
        with pytest.raises(ValueError):
            await service.process_message(
                session_id="test_session_123",
                message=""
            )
    
    @pytest.mark.asyncio
    async def test_get_chat_history(self, mock_mongodb):
        """Test retrieving chat history."""
        from src.services.chat_service import ChatService
        
        service = ChatService()
        mock_mongodb['messages'].find.return_value = [
            {"role": "user", "content": "Test message"},
            {"role": "assistant", "content": "Test response"}
        ]
        
        history = await service.get_chat_history("test_session_123")
        assert isinstance(history, list)

