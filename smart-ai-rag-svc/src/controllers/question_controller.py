"""
Question Controller - Handles question-answering endpoints.

This controller processes questions and returns AI-generated answers
based on indexed documents.
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..models.schemas import QuestionRequest, QuestionResponse
from ..services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/questions",
    tags=["questions"],
    responses={404: {"description": "Not found"}},
)


class QuestionController:
    """Controller for question-answering endpoints."""
    
    def __init__(self, rag_service: EnhancedRAGService):
        """
        Initialize question controller.
        
        Args:
            rag_service: RAG service instance
        """
        self.rag_service = rag_service
        logger.info("QuestionController initialized")
    
    async def ask_question(
        self,
        request: QuestionRequest,
        use_llamaindex: bool = True
    ) -> QuestionResponse:
        """
        Process a question and return an AI-generated answer.
        
        Args:
            request: Question request with question text and options
            use_llamaindex: Whether to use LlamaIndex for querying
            
        Returns:
            QuestionResponse with answer and source information
        """
        try:
            logger.info(f"Processing question: {request.question[:100]}... (LlamaIndex: {use_llamaindex})")
            
            # Process question through service
            result = self.rag_service.ask_question(
                question=request.question,
                k=request.k,
                use_conversation_history=request.use_conversation_history,
                use_llamaindex=use_llamaindex
            )
            
            # Handle error cases
            if not result.get("success", True):
                logger.warning(f"Question processing returned error: {result.get('message')}")
                return QuestionResponse(
                    answer=result.get("answer", "Error processing question."),
                    sources=[],
                    num_sources=0,
                    processing_time=0,
                    timestamp=datetime.now().isoformat(),
                    query_engine=result.get("query_engine", "unknown"),
                    conversation_history_used=request.use_conversation_history
                )
            
            logger.info(f"Successfully processed question with {result.get('num_sources', 0)} sources")
            return QuestionResponse(**result)
            
        except Exception as e:
            logger.error(f"Question processing failed: {str(e)}", exc_info=True)
            # Return a graceful error response instead of raising exception
            return QuestionResponse(
                answer=f"Error processing question: {str(e)[:200]}",
                sources=[],
                num_sources=0,
                processing_time=0.0,
                timestamp=datetime.now().isoformat(),
                query_engine="error",
                conversation_history_used=getattr(request, 'use_conversation_history', False)
            )


# API endpoint functions
_controller: Optional[QuestionController] = None


def init_controller(rag_service: EnhancedRAGService):
    """Initialize controller with dependencies."""
    global _controller
    _controller = QuestionController(rag_service)


@router.post("/ask", response_model=QuestionResponse)
async def ask_question_endpoint(
    request: QuestionRequest,
    use_llamaindex: bool = True
):
    """
    Ask a question and get an AI-generated answer based on indexed documents.
    
    Args:
        request: Question request with question text and options
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False)
    """
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.ask_question(request, use_llamaindex)

