"""
Main FastAPI application for the RAG service.
"""
import logging
from datetime import datetime
from typing import List, Dict, Any
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional
import tempfile
import os

from src.services.enhanced_rag_service import EnhancedRAGService
from src.models.schemas import (
    DocumentUploadRequest, DocumentUploadResponse,
    QuestionRequest, QuestionResponse,
    ConversationMessage, ServiceStatsResponse,
    HealthCheckResponse, EvaluationRequest, EvaluationResponse, EvaluationMetrics
)
from src.config.settings import settings
from src.utils.rag_evaluator import RAGEvaluator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global service instances
rag_service: EnhancedRAGService = None
rag_evaluator: RAGEvaluator = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global rag_service, rag_evaluator
    
    # Startup
    logger.info("Starting services...")
    try:
        rag_service = EnhancedRAGService()
        logger.info("✅ Enhanced RAG service with LlamaIndex initialized successfully")
        
        # Initialize RAG evaluator
        rag_evaluator = RAGEvaluator()
        logger.info("✅ RAG Evaluator initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")


# Create FastAPI app
app = FastAPI(
    title="Smart AI RAG Service",
    description="A Retrieval-Augmented Generation service using LangChain, OpenAI, and MongoDB Vector Search",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", response_model=HealthCheckResponse)
async def root():
    """Root endpoint with basic service information."""
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.get("/health", response_model=HealthCheckResponse)
async def health_check():
    """Health check endpoint."""
    try:
        # Basic health check - could be extended to check database connectivity
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat()
        )
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service unhealthy"
        )


@app.post("/documents/upload-file", response_model=DocumentUploadResponse)
async def upload_file(file: UploadFile = File(...), use_llamaindex: bool = True):
    """
    Upload and index a PDF file directly.
    
    Upload a PDF file and it will be processed and indexed automatically.
    
    Args:
        file: PDF file to upload
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False) for processing
    """
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Only PDF files are supported"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            # Read and write file content
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            logger.info(f"Processing uploaded file: {file.filename} (LlamaIndex: {use_llamaindex})")
            
            result = rag_service.load_and_index_documents(
                file_path=temp_file_path,
                use_llamaindex=use_llamaindex,
                original_filename=file.filename
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
            
            # Add original filename to result
            result["original_filename"] = file.filename
            result["processor_used"] = "llamaindex" if use_llamaindex else "langchain"
            
            return DocumentUploadResponse(**result)
            
        finally:
            # Clean up temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"File upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload file: {str(e)}"
        )


@app.post("/documents/upload-path", response_model=DocumentUploadResponse)
async def upload_documents_by_path(request: DocumentUploadRequest, use_llamaindex: bool = True):
    """
    Upload and index PDF documents by file path.
    
    Provide either file_path for a single PDF or directory_path for multiple PDFs.
    
    Args:
        request: Document upload request with file or directory path
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False) for processing
    """
    try:
        if not request.file_path and not request.directory_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Either file_path or directory_path must be provided"
            )
        
        if request.file_path and request.directory_path:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Provide either file_path or directory_path, not both"
            )
        
        logger.info(f"Processing document upload request: {request} (LlamaIndex: {use_llamaindex})")
        
        result = rag_service.load_and_index_documents(
            file_path=request.file_path,
            directory_path=request.directory_path,
            use_llamaindex=use_llamaindex
        )
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=result["message"]
            )
        
        result["processor_used"] = "llamaindex" if use_llamaindex else "langchain"
        return DocumentUploadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document upload failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload documents: {str(e)}"
        )


@app.post("/questions/ask", response_model=QuestionResponse)
async def ask_question(request: QuestionRequest, use_llamaindex: bool = True):
    """
    Ask a question and get an AI-generated answer based on indexed documents.
    
    Args:
        request: Question request with question text and options
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False) for querying
    """
    try:
        logger.info(f"Processing question: {request.question[:100]}... (LlamaIndex: {use_llamaindex})")
        
        result = rag_service.ask_question(
            question=request.question,
            k=request.k,
            use_conversation_history=request.use_conversation_history,
            use_llamaindex=use_llamaindex
        )
        
        if not result.get("success", True):
            # Handle error case
            return QuestionResponse(
                answer=result.get("answer", "Error processing question."),
                sources=[],
                num_sources=0,
                processing_time=0,
                timestamp=datetime.now().isoformat(),
                query_engine=result.get("query_engine", "unknown"),
                conversation_history_used=request.use_conversation_history
            )
        
        return QuestionResponse(**result)
        
    except Exception as e:
        logger.error(f"Question processing failed: {str(e)}")
        # Return a proper QuestionResponse with all required fields
        return QuestionResponse(
            answer=f"Error processing question: {str(e)[:200]}",
            sources=[],
            num_sources=0,
            processing_time=0.0,
            timestamp=datetime.now().isoformat(),
            query_engine="error",
            conversation_history_used=request.use_conversation_history if hasattr(request, 'use_conversation_history') else False
        )


@app.get("/conversation/history", response_model=List[ConversationMessage])
async def get_conversation_history():
    """Get the current conversation history."""
    try:
        history = rag_service.get_conversation_history()
        return [ConversationMessage(**msg) for msg in history]
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@app.delete("/conversation/history")
async def clear_conversation_history():
    """Clear the conversation history."""
    try:
        rag_service.clear_conversation_history()
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation history: {str(e)}"
        )


@app.get("/stats", response_model=ServiceStatsResponse)
async def get_service_stats():
    """Get service statistics and configuration."""
    try:
        stats = rag_service.get_service_stats()
        
        if "error" in stats:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=stats["error"]
            )
        
        return ServiceStatsResponse(**stats)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get service stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service stats: {str(e)}"
        )




def _get_quality_assessment(overall_quality: float) -> dict:
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


def _get_quality_recommendations(metrics: dict) -> list:
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


@app.post("/evaluate/rag", response_model=EvaluationResponse)
async def evaluate_rag(request: EvaluationRequest):
    """
    Evaluate RAG response quality using TruLens metrics.
    
    Metrics:
    - Answer Relevance: How relevant is the answer to the question?
    - Context Relevance: How relevant is the retrieved context?
    - Groundedness: Is the answer grounded in the context?
    - Overall Quality: Combined quality score
    """
    if rag_evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="RAG Evaluator service not initialized"
        )
    
    try:
        logger.info(f"Evaluating RAG response for question: {request.question[:50]}...")
        
        # Perform evaluation
        result = rag_evaluator.evaluate_rag_response(
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
        logger.error(f"RAG evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to evaluate RAG response: {str(e)}"
        )


@app.post("/evaluate/rag-from-query")
async def evaluate_from_query(
    question: str = Form(...),
    use_llamaindex: bool = Form(True)
):
    """
    Ask a question, get an answer, and evaluate the response quality in one step.
    
    **DEPRECATED:** Use POST /evaluate/query instead (accepts JSON).
    This endpoint uses form-data for compatibility with file upload patterns.
    """
    if rag_service is None or rag_evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized"
        )
    
    try:
        logger.info(f"Processing and evaluating question: {question[:50]}...")
        
        # Get answer from RAG service
        result = rag_service.ask_question(
            question=question,
            use_llamaindex=use_llamaindex,
            use_conversation_history=False
        )
        
        # Extract context from sources
        context = [source.get('content_preview', '') for source in result.get('sources', [])]
        
        # Evaluate the response
        evaluation = rag_evaluator.evaluate_rag_response(
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
                "quality_assessment": _get_quality_assessment(metrics.get('overall_quality', 0)),
                "recommendations": _get_quality_recommendations(metrics)
            },
            "summary_text": rag_evaluator.get_evaluation_summary(evaluation)
        }
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Query and evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and evaluate question: {str(e)}"
        )


@app.post("/evaluate/query")
async def evaluate_query_json(request: QuestionRequest):
    """
    Ask a question, get an answer, and evaluate the response quality (JSON version).
    
    This is the JSON-friendly version of /evaluate/rag-from-query.
    
    Example:
    ```json
    {
      "question": "How many years of experience does gokul have?",
      "use_llamaindex": true,
      "k": 5
    }
    ```
    """
    if rag_service is None or rag_evaluator is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Services not initialized"
        )
    
    try:
        logger.info(f"Processing and evaluating question: {request.question[:50]}...")
        
        # Get answer from RAG service
        result = rag_service.ask_question(
            question=request.question,
            use_llamaindex=request.use_llamaindex,
            k=request.k,
            use_conversation_history=request.use_conversation_history
        )
        
        # Extract context from sources
        context = [source.get('content_preview', '') for source in result.get('sources', [])]
        
        # Evaluate the response
        evaluation = rag_evaluator.evaluate_rag_response(
            question=request.question,
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
                "quality_assessment": _get_quality_assessment(metrics.get('overall_quality', 0)),
                "recommendations": _get_quality_recommendations(metrics)
            },
            "summary_text": rag_evaluator.get_evaluation_summary(evaluation)
        }
        
        return combined_result
        
    except Exception as e:
        logger.error(f"Query and evaluation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process and evaluate question: {str(e)}"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler."""
    logger.error(f"Unhandled exception: {str(exc)}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logger.info("Starting RAG service server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
