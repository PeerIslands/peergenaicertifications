"""
Conversation Controller - Handles conversation history endpoints.

This controller manages conversation history operations including
retrieval and clearing of conversation context.
"""
import logging
from typing import List, Optional

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import JSONResponse

from ..models.schemas import ConversationMessage
from ..services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/conversation",
    tags=["Conversation"],
    responses={404: {"description": "Not found"}},
)


class ConversationController:
    """Controller for conversation history endpoints."""
    
    def __init__(self, rag_service: EnhancedRAGService):
        """
        Initialize conversation controller.
        
        Args:
            rag_service: RAG service instance
        """
        self.rag_service = rag_service
        logger.info("ConversationController initialized")
    
    async def get_history(self) -> List[ConversationMessage]:
        """
        Get conversation history.
        
        Returns:
            List of conversation messages
            
        Raises:
            HTTPException: If retrieval fails
        """
        try:
            history = self.rag_service.get_conversation_history()
            logger.info(f"Retrieved {len(history)} conversation messages")
            return [ConversationMessage(**msg) for msg in history]
            
        except Exception as e:
            logger.error(f"Failed to get conversation history: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get conversation history: {str(e)}"
            )
    
    async def clear_history(self) -> dict:
        """
        Clear conversation history.
        
        Returns:
            Success message
            
        Raises:
            HTTPException: If clearing fails
        """
        try:
            self.rag_service.clear_conversation_history()
            logger.info("Conversation history cleared successfully")
            return {"message": "Conversation history cleared successfully"}
            
        except Exception as e:
            logger.error(f"Failed to clear conversation history: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to clear conversation history: {str(e)}"
            )


# API endpoint functions
_controller: Optional[ConversationController] = None


def init_controller(rag_service: EnhancedRAGService):
    """Initialize controller with dependencies."""
    global _controller
    _controller = ConversationController(rag_service)


@router.get("/history", response_model=List[ConversationMessage])
async def get_history_endpoint():
    """Get the current conversation history."""
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.get_history()


@router.delete("/history")
async def clear_history_endpoint():
    """Clear the conversation history."""
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.clear_history()

