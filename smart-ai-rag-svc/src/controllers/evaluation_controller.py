"""
Evaluation Controller - Handles RAG evaluation endpoints.

This controller processes RAG quality evaluation requests using LangSmith evaluation framework.
"""
import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, status, Form

from ..models.schemas import (
    EvaluationRequest,
    EvaluationResponse,
    EvaluationMetrics,
    QuestionRequest
)
from ..services.enhanced_rag_service import EnhancedRAGService
from ..utils.rag_evaluator import RAGEvaluator

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/evaluate",
    tags=["evaluation"],
    responses={404: {"description": "Not found"}},
)


class EvaluationController:
    """Controller for RAG evaluation endpoints."""
    
    def __init__(
        self,
        rag_service: EnhancedRAGService,
        rag_evaluator: RAGEvaluator
    ):
        """
        Initialize evaluation controller.
        
        Args:
            rag_service: RAG service instance
            rag_evaluator: RAG evaluator instance
        """
        self.rag_service = rag_service
        self.rag_evaluator = rag_evaluator
        logger.info("EvaluationController initialized")
    
    async def evaluate_rag(self, request: EvaluationRequest) -> EvaluationResponse:
        """
        Evaluate RAG response quality.
        
        Args:
            request: Evaluation request with question, answer, and context
            
        Returns:
            EvaluationResponse with quality metrics
            
        Raises:
            HTTPException: If evaluation fails
        """
        try:
            logger.info(f"Evaluating RAG response for question: {request.question[:50]}...")
            
            # Perform evaluation
            result = self.rag_evaluator.evaluate_rag_response(
                question=request.question,
                answer=request.answer,
                context=request.context,
                source_info=request.source_info
            )
            
            # Check for errors in evaluation
            if "error" in result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Evaluation failed: {result['error']}"
                )
            
            # Convert to response model
            metrics = EvaluationMetrics(**result['metrics'])
            
            response = EvaluationResponse(
                question=result['question'],
                answer=result['answer'],
                metrics=metrics,
                context_stats=result['context_stats'],
                evaluation_time=result['evaluation_time'],
                timestamp=result['timestamp']
            )
            
            logger.info(f"Evaluation complete. Overall quality: {metrics.overall_quality:.2f}")
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"RAG evaluation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to evaluate RAG response: {str(e)}"
            )
    
    async def evaluate_from_query_json(self, request: QuestionRequest) -> dict:
        """
        Ask question and evaluate response (JSON version).
        
        Args:
            request: Question request
            
        Returns:
            Combined RAG response and evaluation results
        """
        return await self._evaluate_from_query(
            request.question,
            request.use_llamaindex
        )
    
    async def _evaluate_from_query(
        self,
        question: str,
        use_llamaindex: bool
    ) -> dict:
        """
        Internal method to process question and evaluate response.
        
        Args:
            question: Question to ask
            use_llamaindex: Whether to use LlamaIndex
            
        Returns:
            Combined RAG response and evaluation results
        """
        try:
            logger.info(f"Processing and evaluating question: {question[:50]}...")
            
            # Get answer from RAG service
            result = self.rag_service.ask_question(
                question=question,
                use_llamaindex=use_llamaindex,
                use_conversation_history=False
            )
            
            # Extract context from sources
            context = [source.get('content_preview', '') for source in result.get('sources', [])]
            
            # Evaluate the response
            evaluation = self.rag_evaluator.evaluate_rag_response(
                question=question,
                answer=result.get('answer', ''),
                context=context,
                source_info=result.get('sources')
            )
            
            # Combine results with structured summary
            metrics = evaluation.get('metrics', {})
            combined_result = {
                "rag_response": result,
                "evaluation": evaluation,
                "summary": {
                    "quality_metrics": metrics,
                    "context_statistics": evaluation.get('context_stats', {}),
                    "evaluation_time_seconds": evaluation.get('evaluation_time', 0),
                    "timestamp": evaluation.get('timestamp', ''),
                    "quality_assessment": self._get_quality_assessment(metrics.get('overall_quality', 0)),
                    "recommendations": self._get_quality_recommendations(metrics)
                },
                "summary_text": self.rag_evaluator.get_evaluation_summary(evaluation)
            }
            
            logger.info(f"Question evaluated successfully. Quality: {metrics.get('overall_quality', 0):.2f}")
            return combined_result
            
        except Exception as e:
            logger.error(f"Query and evaluation failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to process and evaluate question: {str(e)}"
            )
    
    def _get_quality_assessment(self, overall_quality: float) -> dict:
        """Get quality assessment based on overall score."""
        if overall_quality >= 0.8:
            return {
                "level": "excellent",
                "message": "Excellent quality response!",
                "score_range": "0.8-1.0"
            }
        elif overall_quality >= 0.6:
            return {
                "level": "good",
                "message": "Good quality response",
                "score_range": "0.6-0.8"
            }
        elif overall_quality >= 0.4:
            return {
                "level": "fair",
                "message": "Fair quality - could be improved",
                "score_range": "0.4-0.6"
            }
        else:
            return {
                "level": "poor",
                "message": "Poor quality - needs improvement",
                "score_range": "0.0-0.4"
            }
    
    def _get_quality_recommendations(self, metrics: dict) -> list:
        """Get recommendations based on metric scores."""
        recommendations = []
        
        answer_relevance = metrics.get('answer_relevance', 0)
        context_relevance = metrics.get('context_relevance', 0)
        groundedness = metrics.get('groundedness', 0)
        
        if answer_relevance < 0.5:
            recommendations.append({
                "issue": "Low Answer Relevance",
                "score": answer_relevance,
                "problem": "Answer doesn't directly address the question",
                "solutions": [
                    "Improve the prompt/query template",
                    "Adjust LLM parameters (temperature, max_tokens)",
                    "Use a more capable LLM model (e.g., gpt-4)"
                ]
            })
        
        if context_relevance < 0.5:
            recommendations.append({
                "issue": "Low Context Relevance",
                "score": context_relevance,
                "problem": "Retrieved documents are not relevant to the question",
                "solutions": [
                    "Improve document chunking (adjust chunk_size or sentence_window_size)",
                    "Use a better embedding model",
                    "Lower the similarity threshold",
                    "Add metadata filtering to improve retrieval"
                ]
            })
        
        if groundedness < 0.5:
            recommendations.append({
                "issue": "Low Groundedness",
                "score": groundedness,
                "problem": "Answer contains information not supported by the context (hallucination)",
                "solutions": [
                    "Add stricter system prompts ('Only use provided context')",
                    "Reduce LLM temperature for more deterministic responses",
                    "Increase the number of context chunks (top_k)",
                    "Enable citation requirements in responses"
                ]
            })
        
        if not recommendations:
            recommendations.append({
                "issue": "None",
                "message": "All metrics are within acceptable ranges!",
                "keep_improving": [
                    "Monitor quality over time",
                    "Test with diverse questions",
                    "Gather user feedback"
                ]
            })
        
        return recommendations


# API endpoint functions
_controller: Optional[EvaluationController] = None


def init_controller(
    rag_service: EnhancedRAGService,
    rag_evaluator: RAGEvaluator
):
    """Initialize controller with dependencies."""
    global _controller
    _controller = EvaluationController(rag_service, rag_evaluator)


@router.post("/rag", response_model=EvaluationResponse)
async def evaluate_rag_endpoint(request: EvaluationRequest):
    """
    Evaluate RAG response quality using LangSmith evaluation metrics.
    
    Metrics:
    - Answer Relevance: How relevant is the answer to the question?
    - Context Relevance: How relevant is the retrieved context?
    - Groundedness: Is the answer grounded in the context?
    - Overall Quality: Combined quality score
    """
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.evaluate_rag(request)


@router.post("/query")
async def evaluate_from_query_json_endpoint(request: QuestionRequest):
    """
    Ask a question, get an answer, and evaluate the response quality (JSON version).
    
    Example:
    ```json
    {
      "question": "How many years of experience does gokul have?",
      "use_llamaindex": true,
      "k": 5
    }
    ```
    """
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.evaluate_from_query_json(request)

