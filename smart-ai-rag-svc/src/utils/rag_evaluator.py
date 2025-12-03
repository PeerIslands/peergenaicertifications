"""
RAG Evaluator using LangSmith for Quality Assessment.

This module provides comprehensive evaluation of RAG (Retrieval-Augmented Generation)
responses using LangSmith evaluation framework. It evaluates multiple quality dimensions
including answer relevance, context relevance, and groundedness.

Classes:
    RAGEvaluator: Main class for evaluating RAG response quality.

Example:
    ```python
    evaluator = RAGEvaluator()
    result = evaluator.evaluate_rag_response(
        question="What is AI?",
        answer="AI is artificial intelligence...",
        context=["AI is...", "Machine learning..."]
    )
    print(evaluator.get_evaluation_summary(result))
    ```
"""
# Suppress warnings before imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

import logging
import time
from typing import Dict, Any, List, Optional
from datetime import datetime
import os

from langchain_openai import ChatOpenAI
from langchain.evaluation import QAEvalChain, CriteriaEvalChain
import numpy as np

from ..config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class RAGEvaluator:
    """
    Evaluator for RAG (Retrieval-Augmented Generation) responses using LangSmith.
    
    Evaluates:
    - Answer Relevance: How relevant is the answer to the question?
    - Context Relevance: How relevant is the retrieved context?
    - Groundedness: Is the answer grounded in the provided context?
    - Overall Quality: Combined quality score
    
    Uses LangSmith's evaluation framework for consistent, production-ready evaluation.
    """
    
    def __init__(self, llm=None):
        """
        Initialize LangSmith evaluator with evaluation chains.
        
        Sets up LangChain evaluation chains for assessing RAG responses.
        The evaluator uses OpenAI's API to assess quality metrics including
        relevance and groundedness.
        
        Args:
            llm: Optional ChatOpenAI instance to reuse. If not provided, will create one.
        
        Raises:
            ValueError: If OpenAI API key is not configured.
            Exception: If LangSmith initialization fails.
        
        Note:
            Requires OPENAI_API_KEY to be set in environment variables.
            Optionally set LANGSMITH_API_KEY for LangSmith tracing and monitoring.
        """
        self._available = False
        self.llm = llm
        self.qa_evaluator = None
        self.criteria_evaluator = None
        
        try:
            if not settings.openai_api_key:
                raise ValueError("OPENAI_API_KEY is required for RAG evaluation")
            
            # Use provided LLM or create a new one
            if self.llm is None:
                # Ensure environment variable is set to avoid 'proxies' argument issues
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
                
                # Try multiple initialization patterns for compatibility
                # Use environment variable instead of passing api_key directly
                llm_initialized = False
                initialization_methods = [
                    # Pattern 1: Minimal - use environment variable only
                    lambda: ChatOpenAI(temperature=0.0),
                    # Pattern 2: With model parameter
                    lambda: ChatOpenAI(model=settings.llm_model, temperature=0.0),
                    # Pattern 3: With model_name parameter (legacy)
                    lambda: ChatOpenAI(model_name=settings.llm_model, temperature=0.0),
                    # Pattern 4: Explicit api_key as last resort
                    lambda: ChatOpenAI(openai_api_key=settings.openai_api_key, temperature=0.0),
                ]
                
                for attempt in initialization_methods:
                    try:
                        self.llm = attempt()
                        # Verify LLM is actually usable
                        if self.llm is not None:
                            llm_initialized = True
                            break
                    except Exception as e:
                        error_msg = str(e)
                        logger.debug(f"LLM initialization attempt failed: {error_msg}")
                        # If it's the proxies error, skip and try next method
                        if "proxies" in error_msg.lower():
                            continue
                        # For other errors, also continue to next method
                        continue
                
                if not llm_initialized:
                    logger.warning("Failed to initialize LLM for evaluation with all methods")
                    self._available = False
                    self.llm = None
                    return
            else:
                # LLM was provided, verify it's usable
                try:
                    # Quick test to see if LLM is callable
                    if hasattr(self.llm, 'invoke') or hasattr(self.llm, '__call__'):
                        llm_initialized = True
                    else:
                        llm_initialized = False
                except Exception:
                    llm_initialized = False
            
            if llm_initialized:
                self._available = True
                logger.info("LangSmith RAG Evaluator initialized successfully")
            
            # Initialize evaluation chains (optional - we use LLM directly for evaluation)
            if self._available and self.llm:
                try:
                    # QA Evaluator for answer correctness (optional)
                    self.qa_evaluator = QAEvalChain.from_llm(self.llm)
                    logger.debug("QA evaluation chain initialized")
                except Exception as qa_error:
                    logger.debug(f"QA evaluation chain not available: {str(qa_error)}")
                    self.qa_evaluator = None
                
                try:
                    # Criteria Evaluator (optional)
                    self.criteria_evaluator = CriteriaEvalChain.from_llm(
                        self.llm,
                        criteria="relevance"
                    )
                    logger.debug("Criteria evaluation chain initialized")
                except Exception as criteria_error:
                    logger.debug(f"Criteria evaluation chain not available: {str(criteria_error)}")
                    self.criteria_evaluator = None
            
        except ValueError as ve:
            logger.warning(f"RAG Evaluator not initialized: {str(ve)}")
            self._available = False
        except Exception as e:
            logger.warning(
                f"Failed to initialize LangSmith evaluator: {str(e)}. "
                f"Evaluation features will be unavailable."
            )
            self._available = False
    
    def evaluate_rag_response(
        self,
        question: str,
        answer: str,
        context: List[str],
        source_info: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluate a RAG response using LangSmith evaluation framework.
        
        Args:
            question: The user's question
            answer: The generated answer
            context: List of context chunks used
            source_info: Optional metadata about sources
            
        Returns:
            Dictionary with evaluation metrics and stats
        """
        if not self._available or not self.llm:
            return {
                "error": "RAG Evaluator is not available. Please check OPENAI_API_KEY configuration.",
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "answer": answer,
                "available": False
            }
        
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
                "timestamp": datetime.now().isoformat(),
                "evaluator": "langsmith"
            }
            
            # Add source info if provided
            if source_info:
                result["source_info"] = source_info
            
            logger.info(
                f"Evaluation complete - "
                f"Answer: {answer_relevance:.2f}, "
                f"Context: {context_relevance:.2f}, "
                f"Groundedness: {groundedness:.2f}, "
                f"Overall: {overall_quality:.2f}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Evaluation failed: {str(e)}", exc_info=True)
            return {
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def _calculate_answer_relevance(self, question: str, answer: str) -> float:
        """
        Calculate how relevant the answer is to the question.
        
        Uses LLM-based evaluation to determine if the answer directly
        addresses the question. Higher scores indicate better alignment.
        
        Args:
            question: The user's original question.
            answer: The generated answer to evaluate.
            
        Returns:
            Relevance score between 0.0 and 1.0, where:
            - 1.0: Answer perfectly addresses the question
            - 0.5: Answer partially addresses the question
            - 0.0: Answer is irrelevant or calculation failed
        """
        if not self._available or not self.llm:
            return 0.0
        
        try:
            logger.debug(f"Calculating answer relevance for question: {question[:50]}...")
            
            # Use LLM to evaluate relevance
            prompt = f"""Evaluate how relevant the answer is to the question.
Question: {question}
Answer: {answer}

Rate the relevance on a scale of 0.0 to 1.0, where:
- 1.0 = Answer perfectly addresses the question
- 0.5 = Answer partially addresses the question
- 0.0 = Answer is irrelevant

Respond with only a number between 0.0 and 1.0:"""
            
            response = self.llm.invoke(prompt)
            score_text = response.content.strip()
            
            # Extract score from response
            try:
                score = float(score_text)
                # Clamp to [0, 1]
                score = max(0.0, min(1.0, score))
            except ValueError:
                # If LLM didn't return a number, try to extract it
                import re
                match = re.search(r'(\d+\.?\d*)', score_text)
                if match:
                    score = float(match.group(1)) / 10.0 if float(match.group(1)) > 1 else float(match.group(1))
                    score = max(0.0, min(1.0, score))
                else:
                    score = 0.5  # Default to neutral if can't parse
            
            logger.debug(f"Answer relevance score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.warning(
                f"Answer relevance calculation failed: {str(e)}",
                exc_info=True
            )
            return 0.0
    
    def _calculate_context_relevance(self, question: str, context: List[str]) -> float:
        """Calculate average relevance of context chunks to the question."""
        if not self._available or not self.llm:
            return 0.0
        
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
        if not self._available or not self.llm:
            return 0.0
        
        try:
            # Use LLM to evaluate context relevance
            prompt = f"""Evaluate how relevant this context is to the question.
Question: {question}
Context: {context[:500]}

Rate the relevance on a scale of 0.0 to 1.0, where:
- 1.0 = Context is highly relevant
- 0.5 = Context is somewhat relevant
- 0.0 = Context is irrelevant

Respond with only a number between 0.0 and 1.0:"""
            
            response = self.llm.invoke(prompt)
            score_text = response.content.strip()
            
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))
            except ValueError:
                import re
                match = re.search(r'(\d+\.?\d*)', score_text)
                if match:
                    score = float(match.group(1)) / 10.0 if float(match.group(1)) > 1 else float(match.group(1))
                    score = max(0.0, min(1.0, score))
                else:
                    score = 0.5
            
            return score
        except Exception as e:
            logger.warning(f"Single context relevance calculation failed: {str(e)}")
            return 0.0
    
    def _calculate_groundedness(self, answer: str, context: str) -> float:
        """
        Calculate if the answer is grounded in the provided context.
        
        Groundedness measures whether the answer's claims are supported by
        the context. Low groundedness indicates hallucination or unsupported
        claims.
        
        Args:
            answer: The generated answer to evaluate.
            context: The context text that should support the answer.
            
        Returns:
            Groundedness score between 0.0 and 1.0, where:
            - 1.0: All answer claims are fully supported by context
            - 0.5: Some claims are supported, some are not
            - 0.0: Answer contains unsupported claims (hallucination) or calculation failed
        """
        if not self._available or not self.llm:
            return 0.0
        
        try:
            logger.debug("Calculating groundedness score...")
            
            # Use LLM to evaluate groundedness
            prompt = f"""Evaluate if the answer is grounded in the provided context.
Context: {context[:1000]}
Answer: {answer}

Rate the groundedness on a scale of 0.0 to 1.0, where:
- 1.0 = All claims in the answer are fully supported by the context
- 0.5 = Some claims are supported, some are not
- 0.0 = Answer contains unsupported claims (hallucination)

Respond with only a number between 0.0 and 1.0:"""
            
            response = self.llm.invoke(prompt)
            score_text = response.content.strip()
            
            try:
                score = float(score_text)
                score = max(0.0, min(1.0, score))
            except ValueError:
                import re
                match = re.search(r'(\d+\.?\d*)', score_text)
                if match:
                    score = float(match.group(1)) / 10.0 if float(match.group(1)) > 1 else float(match.group(1))
                    score = max(0.0, min(1.0, score))
                else:
                    score = 0.5
            
            logger.debug(f"Groundedness score: {score:.3f}")
            return score
            
        except Exception as e:
            logger.warning(
                f"Groundedness calculation failed: {str(e)}",
                exc_info=True
            )
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
            return f"ERROR - Evaluation Error: {eval_result['error']}"
        
        metrics = eval_result.get('metrics', {})
        context_stats = eval_result.get('context_stats', {})
        
        summary = [
            "\n" + "="*60,
            "RAG EVALUATION SUMMARY (LangSmith)",
            "="*60,
            "",
            "Quality Metrics:",
            f"  • Answer Relevance:  {metrics.get('answer_relevance', 0):.2f} / 1.00",
            f"  • Context Relevance: {metrics.get('context_relevance', 0):.2f} / 1.00",
            f"  • Groundedness:      {metrics.get('groundedness', 0):.2f} / 1.00",
            f"  • Overall Quality:   {metrics.get('overall_quality', 0):.2f} / 1.00",
            "",
            "Context Statistics:",
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
            summary.append("[EXCELLENT] Excellent quality response!")
        elif overall >= 0.6:
            summary.append("✔️  Good quality response")
        elif overall >= 0.4:
            summary.append("[FAIR] Fair quality - could be improved")
        else:
            summary.append("[POOR] Poor quality - needs improvement")
        
        summary.append("="*60 + "\n")
        
        return "\n".join(summary)
