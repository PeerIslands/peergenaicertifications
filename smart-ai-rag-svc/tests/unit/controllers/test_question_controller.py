"""
Unit tests for QuestionController.
"""
import pytest
from unittest.mock import MagicMock

from src.controllers.question_controller import QuestionController
from src.models.schemas import QuestionRequest


class TestQuestionController:
    """Test QuestionController class."""
    
    @pytest.fixture
    def controller(self, mock_rag_service):
        """Create QuestionController instance."""
        return QuestionController(mock_rag_service)
    
    @pytest.mark.asyncio
    async def test_ask_question_success(self, controller, mock_rag_service):
        """Test successful question answering."""
        request = QuestionRequest(
            question="What is this about?",
            k=5,
            use_conversation_history=False
        )
        
        result = await controller.ask_question(request, use_llamaindex=True)
        
        assert result.answer is not None
        assert result.num_sources >= 0
        assert mock_rag_service.ask_question.called
    
    @pytest.mark.asyncio
    async def test_ask_question_with_history(self, controller, mock_rag_service):
        """Test question with conversation history."""
        request = QuestionRequest(
            question="Follow-up question",
            use_conversation_history=True
        )
        
        result = await controller.ask_question(request)
        
        assert result is not None
        call_args = mock_rag_service.ask_question.call_args
        assert call_args[1]['use_conversation_history'] is True
    
    @pytest.mark.asyncio
    async def test_ask_question_error_handling(self, controller, mock_rag_service):
        """Test error handling in question processing."""
        mock_rag_service.ask_question.return_value = {
            "success": False,
            "message": "Error processing question"
        }
        
        request = QuestionRequest(question="Test question")
        result = await controller.ask_question(request)
        
        assert result.answer is not None
        assert result.num_sources == 0

