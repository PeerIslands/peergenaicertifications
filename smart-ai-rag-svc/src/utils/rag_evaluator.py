"""
RAG Evaluator using TruLens for quality assessment.
"""
import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime

from trulens.core import Tru, Feedback
from trulens.providers.openai import OpenAI as TruLensOpenAI
import numpy as np

from ..config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Evaluator for RAG (Retrieval-Augmented Generation) responses using TruLens.
    
    Evaluates:
    - Answer Relevance: How relevant is the answer to the question?
    - Context Relevance: How relevant is the retrieved context?
    - Groundedness: Is the answer grounded in the provided context?
    - Overall Quality: Combined quality score
    """
    
    def __init__(self):
        """Initialize TruLens evaluator with feedback functions."""
        try:
            # Initialize Tru database
            self.tru = Tru()
            
            # Initialize OpenAI provider for feedback
            self.openai_provider = TruLensOpenAI(api_key=settings.openai_api_key)
            
            logger.info("✅ TruLens RAG Evaluator initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize TruLens evaluator: {str(e)}")
            raise
    
    def evaluate_rag_response(
        self,
        question: str,
        answer: str,
        context: List[str],
        source_info: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a RAG response using TruLens feedback functions.
        
        Args:
            question: The user's question
            answer: The generated answer
            context: List of context chunks used
            source_info: Optional metadata about sources
            
        Returns:
            Dictionary with evaluation metrics and stats
        """
        try:
            start_time = time.time()
            
            # Prepare context as a single string
            context_text = "\n\n".join(context)
            
            # Calculate individual metrics
            logger.info("Calculating answer relevance...")
            answer_relevance = self._calculate_answer_relevance(question, answer)
            
            logger.info("Calculating context relevance...")
            context_relevance = self._calculate_context_relevance(question, context)
            
            logger.info("Calculating groundedness...")
            groundedness = self._calculate_groundedness(answer, context_text)
            
            # Calculate overall quality (weighted average)
            overall_quality = (
                answer_relevance * 0.35 +
                context_relevance * 0.30 +
                groundedness * 0.35
            )
            
            evaluation_time = time.time() - start_time
            
            # Prepare response
            result = {
                "question": question,
                "answer": answer,
                "metrics": {
                    "answer_relevance": round(answer_relevance, 3),
                    "context_relevance": round(context_relevance, 3),
                    "groundedness": round(groundedness, 3),
                    "overall_quality": round(overall_quality, 3)
                },
                "context_stats": {
                    "num_chunks": len(context),
                    "total_chars": sum(len(c) for c in context),
                    "avg_chunk_length": int(np.mean([len(c) for c in context])) if context else 0,
                    "context_relevance_scores": [
                        round(self._calculate_single_context_relevance(question, c), 3)
                        for c in context[:5]  # Limit to first 5 for performance
                    ]
                },
                "evaluation_time": round(evaluation_time, 2),
                "timestamp": datetime.now().isoformat()
            }
            
            # Add source info if provided
            if source_info:
                result["source_info"] = source_info
            
            logger.info(
                f"✅ Evaluation complete - "
                f"Answer: {answer_relevance:.2f}, "
                f"Context: {context_relevance:.2f}, "
                f"Groundedness: {groundedness:.2f}, "
                f"Overall: {overall_quality:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}")
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_answer_relevance(self, question: str, answer: str) -> float:
        """Calculate how relevant the answer is to the question."""
        try:
            score = self.openai_provider.relevance(
                prompt=question,
                response=answer
            )
            return float(score) if score is not None else 0.0
        except Exception as e:
            logger.warning(f"Answer relevance calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_context_relevance(self, question: str, context: List[str]) -> float:
        """Calculate average relevance of context chunks to the question."""
        try:
            if not context:
                return 0.0
            
            scores = []
            for chunk in context[:5]:  # Limit to first 5 for performance
                score = self._calculate_single_context_relevance(question, chunk)
                scores.append(score)
            
            return float(np.mean(scores)) if scores else 0.0
        except Exception as e:
            logger.warning(f"Context relevance calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_single_context_relevance(self, question: str, context: str) -> float:
        """Calculate relevance of a single context chunk."""
        try:
            # Use the correct TruLens API method
            score = self.openai_provider.relevance(
                prompt=question,
                response=context
            )
            return float(score) if score is not None else 0.0
        except Exception as e:
            logger.warning(f"Single context relevance calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_groundedness(self, answer: str, context: str) -> float:
        """Calculate if the answer is grounded in the context."""
        try:
            score = self.openai_provider.groundedness_measure_with_cot_reasons(
                source=context,
                statement=answer
            )
            # Extract score from tuple if returned
            if isinstance(score, tuple):
                return float(score[0]) if score[0] is not None else 0.0
            return float(score) if score is not None else 0.0
        except Exception as e:
            logger.warning(f"Groundedness calculation failed: {str(e)}")
            return 0.0
    
    def get_evaluation_summary(self, eval_result: Dict[str, Any]) -> str:
        """
        Format evaluation results into a readable summary.
        
        Args:
            eval_result: Result from evaluate_rag_response()
            
        Returns:
            Formatted string summary
        """
        if "error" in eval_result:
            return f"❌ Evaluation Error: {eval_result['error']}"
        
        metrics = eval_result.get('metrics', {})
        context_stats = eval_result.get('context_stats', {})
        
        summary = [
            "\n" + "="*60,
            "📊 RAG EVALUATION SUMMARY",
            "="*60,
            "",
            "🎯 Quality Metrics:",
            f"  • Answer Relevance:  {metrics.get('answer_relevance', 0):.2f} / 1.00",
            f"  • Context Relevance: {metrics.get('context_relevance', 0):.2f} / 1.00",
            f"  • Groundedness:      {metrics.get('groundedness', 0):.2f} / 1.00",
            f"  • Overall Quality:   {metrics.get('overall_quality', 0):.2f} / 1.00",
            "",
            "📚 Context Statistics:",
            f"  • Number of chunks:  {context_stats.get('num_chunks', 0)}",
            f"  • Total characters:  {context_stats.get('total_chars', 0):,}",
            f"  • Avg chunk length:  {context_stats.get('avg_chunk_length', 0)}",
            "",
            f"⏱️  Evaluation Time: {eval_result.get('evaluation_time', 0):.2f}s",
            "="*60,
        ]
        
        # Add quality interpretation
        overall = metrics.get('overall_quality', 0)
        if overall >= 0.8:
            summary.append("✅ Excellent quality response!")
        elif overall >= 0.6:
            summary.append("✔️  Good quality response")
        elif overall >= 0.4:
            summary.append("⚠️  Fair quality - could be improved")
        else:
            summary.append("❌ Poor quality - needs improvement")
        
        summary.append("="*60 + "\n")
        
        return "\n".join(summary)
