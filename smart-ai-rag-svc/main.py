"""
Main FastAPI application for the RAG service.
"""
# Suppress warnings BEFORE any imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pkg_resources.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")
warnings.filterwarnings("ignore", message=".*Context is being overwritten.*")
warnings.filterwarnings("ignore", message=".*Secret keys may be written.*")
warnings.filterwarnings("ignore", category=UserWarning, module="munch")

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

# Suppress deprecation warnings from dependencies
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pkg_resources")
warnings.filterwarnings("ignore", message=".*pkg_resources.*", category=UserWarning)
warnings.filterwarnings("ignore", message=".*LangChainDeprecationWarning.*")
warnings.filterwarnings("ignore", message=".*Context is being overwritten.*")

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
        if rag_service._llamaindex_available:
            logger.info("Enhanced RAG service initialized (LlamaIndex + LangChain available)")
        else:
            logger.info("Enhanced RAG service initialized (LangChain only - set OPENAI_API_KEY for LlamaIndex)")
        
        # Initialize RAG evaluator (optional - requires OpenAI API key)
        # Reuse LLM from rag_service if available to avoid initialization issues
        try:
            if settings.openai_api_key and rag_service and rag_service.llm:
                # Reuse LLM from rag_service to avoid ChatOpenAI initialization issues
                rag_evaluator = RAGEvaluator(llm=rag_service.llm)
                if rag_evaluator._available:
                    logger.info("LangSmith RAG Evaluator initialized successfully (reusing LLM)")
                else:
                    logger.warning("RAG Evaluator initialized but not fully available")
            elif settings.openai_api_key:
                # Try to create evaluator with new LLM
                try:
                    rag_evaluator = RAGEvaluator()
                    if rag_evaluator._available:
                        logger.info("LangSmith RAG Evaluator initialized successfully")
                    else:
                        logger.warning("RAG Evaluator initialized but not fully available")
                except Exception:
                    logger.warning("RAG Evaluator initialization failed")
                    rag_evaluator = None
            else:
                logger.warning("RAG Evaluator not initialized (OPENAI_API_KEY required)")
                rag_evaluator = None
        except Exception as eval_error:
            logger.warning(f"RAG Evaluator initialization failed: {str(eval_error)}")
            rag_evaluator = None
    except Exception as e:
        logger.error(f"Failed to initialize services: {str(e)}")
        # Don't raise - allow app to start even if some services fail
        # This allows health checks and basic functionality
        logger.warning("Application starting with limited functionality")
    
    yield
    
    # Shutdown
    logger.info("Shutting down services...")


# Create FastAPI app with comprehensive OpenAPI documentation
app = FastAPI(
    title="Smart AI RAG Service",
    description="""
    ## Smart AI RAG (Retrieval-Augmented Generation) Service
    
    A production-ready RAG service that combines **LangChain** and **LlamaIndex** frameworks
    for intelligent document processing and question answering.
    
    ### Key Features
    
    * **Document Processing**: Upload and index PDF documents
    * **AI-Powered Q&A**: Ask questions and get intelligent answers
    * **Vector Search**: MongoDB Atlas vector search for semantic retrieval
    * **Quality Evaluation**: LangSmith-based RAG quality assessment
    * **Conversation History**: Maintain context across multiple questions
    
    ### Frameworks
    
    * **LangChain**: Traditional document processing and chunking
    * **LlamaIndex**: Advanced sentence-window based processing (recommended)
    * **OpenAI**: GPT models for text generation and embeddings
    * **MongoDB Atlas**: Vector database for document storage
    
    ### Quick Start
    
    1. Upload a PDF document: `POST /documents/upload-file`
    2. Ask a question: `POST /questions/ask`
    3. Evaluate quality: `POST /evaluate/query`
    
    ### Authentication
    
    Currently open access. Production deployments should implement API key authentication.
    """,
    version="2.0.0",
    lifespan=lifespan,
    contact={
        "name": "Smart AI RAG Service",
        "url": "https://github.com/your-org/smart-ai-rag-svc",
    },
    license_info={
        "name": "MIT",
    },
    servers=[
        {
            "url": "http://localhost:8000",
            "description": "Development server"
        },
        {
            "url": "https://api.yourdomain.com",
            "description": "Production server"
        }
    ],
    tags_metadata=[
        {
            "name": "health",
            "description": "Health check and service status endpoints.",
        },
        {
            "name": "documents",
            "description": "Document upload and management operations. Upload PDF files to index them for retrieval.",
        },
        {
            "name": "questions",
            "description": "Question answering endpoints. Ask questions and get AI-generated answers based on indexed documents.",
        },
        {
            "name": "conversation",
            "description": "Conversation history management. Track and manage multi-turn conversations.",
        },
        {
            "name": "evaluation",
            "description": "RAG quality evaluation using LangSmith metrics. Assess answer relevance, context relevance, and groundedness.",
        },
    ],
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get(
    "/",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Root endpoint",
    description="Returns basic service information and health status.",
    response_description="Service health status and version information"
)
async def root():
    """
    Root endpoint with basic service information.
    
    Returns:
        HealthCheckResponse: Service status and version
    """
    return HealthCheckResponse(
        status="healthy",
        timestamp=datetime.now().isoformat()
    )


@app.get(
    "/health",
    response_model=HealthCheckResponse,
    tags=["health"],
    summary="Health check",
    description="Check if the service is running and healthy. Used by load balancers and monitoring systems.",
    response_description="Service health status"
)
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    Returns:
        HealthCheckResponse: Current health status
        
    Note:
        This endpoint performs a basic health check. For detailed dependency
        checks, use the /health/ready endpoint (if implemented).
    """
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


@app.post(
    "/documents/upload-file",
    response_model=DocumentUploadResponse,
    tags=["documents"],
    summary="Upload PDF file",
    description="""
    Upload a PDF file directly through the API.
    
    The file will be:
    1. Validated (must be a PDF)
    2. Processed and chunked
    3. Embedded using OpenAI embeddings
    4. Indexed in MongoDB vector store
    
    **Recommended**: Use `use_llamaindex=True` for better processing.
    """,
    response_description="Upload and indexing results with statistics"
)
async def upload_file(
    file: UploadFile = File(..., description="PDF file to upload and index"),
    use_llamaindex: bool = True
):
    """
    Upload and index a PDF file directly.
    
    Args:
        file: PDF file to upload (multipart/form-data)
        use_llamaindex: Whether to use LlamaIndex (True, recommended) or LangChain (False)
    
    Returns:
        DocumentUploadResponse: Upload results with statistics
        
    Raises:
        400: If file is not a PDF
        500: If processing fails
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


@app.post(
    "/documents/upload-path",
    response_model=DocumentUploadResponse,
    tags=["documents"],
    summary="Upload documents by file path",
    description="""
    Upload and index PDF documents by providing a file system path.
    
    **Use Cases:**
    - Server-side file processing
    - Batch document indexing
    - Automated document ingestion
    
    **Note:** This endpoint requires the file to be accessible from the server.
    For client uploads, use `/documents/upload-file` instead.
    
    **Processing Options:**
    - Single file: Provide `file_path`
    - Multiple files: Provide `directory_path` (all PDFs in directory)
    """,
    response_description="Upload and indexing results"
)
async def upload_documents_by_path(
    request: DocumentUploadRequest,
    use_llamaindex: bool = True
):
    """
    Upload and index PDF documents by file path.
    
    Args:
        request: Document upload request with file or directory path
        use_llamaindex: Whether to use LlamaIndex (True, recommended) or LangChain (False)
    
    Returns:
        DocumentUploadResponse: Upload results with statistics
        
    Raises:
        400: If neither path is provided or both are provided
        404: If file or directory doesn't exist
        500: If processing fails
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


@app.post(
    "/questions/ask",
    response_model=QuestionResponse,
    tags=["questions"],
    summary="Ask a question",
    description="""
    Ask a question and get an AI-generated answer based on indexed documents.
    
    The service will:
    1. Retrieve relevant document chunks using vector similarity search
    2. Generate an answer using the configured LLM (GPT-3.5-turbo or GPT-4)
    3. Return the answer with source citations
    
    **Use Cases:**
    - Document Q&A: "What skills does the candidate have?"
    - Information extraction: "What is the candidate's experience?"
    - Summarization: "Summarize the main points"
    """,
    response_description="AI-generated answer with source citations"
)
async def ask_question(
    request: QuestionRequest,
    use_llamaindex: bool = True
):
    """
    Ask a question and get an AI-generated answer based on indexed documents.
    
    Args:
        request: Question request with question text and options
        use_llamaindex: Whether to use LlamaIndex (True, recommended) or LangChain (False)
    
    Returns:
        QuestionResponse: Answer with sources and metadata
        
    Example Request:
        ```json
        {
            "question": "What is the main topic?",
            "k": 5,
            "use_conversation_history": false,
            "use_llamaindex": true
        }
        ```
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


@app.get(
    "/conversation/history",
    response_model=List[ConversationMessage],
    tags=["conversation"],
    summary="Get conversation history",
    description="""
    Retrieve the current conversation history.
    
    Returns all messages in the conversation, including both user questions
    and AI responses. Useful for:
    - Displaying chat history in UI
    - Debugging conversation flow
    - Analyzing conversation patterns
    """,
    response_description="List of conversation messages"
)
async def get_conversation_history():
    """
    Get the current conversation history.
    
    Returns:
        List[ConversationMessage]: All messages in the conversation
        
    Note:
        Conversation history is stored in memory and cleared on service restart.
        Use this endpoint to retrieve history before asking follow-up questions
        with `use_conversation_history=True`.
    """
    try:
        history = rag_service.get_conversation_history()
        return [ConversationMessage(**msg) for msg in history]
        
    except Exception as e:
        logger.error(f"Failed to get conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get conversation history: {str(e)}"
        )


@app.delete(
    "/conversation/history",
    tags=["conversation"],
    summary="Clear conversation history",
    description="""
    Clear all conversation history.
    
    Removes all stored conversation messages from memory. Useful for:
    - Starting a new conversation session
    - Resetting context
    - Privacy compliance (clearing user data)
    """,
    response_description="Confirmation message"
)
async def clear_conversation_history():
    """
    Clear the conversation history.
    
    Returns:
        dict: Success message
        
    Note:
        This operation cannot be undone. All conversation context will be lost.
    """
    try:
        rag_service.clear_conversation_history()
        return {"message": "Conversation history cleared successfully"}
        
    except Exception as e:
        logger.error(f"Failed to clear conversation history: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to clear conversation history: {str(e)}"
        )


@app.get(
    "/stats",
    response_model=ServiceStatsResponse,
    tags=["health"],
    summary="Get service statistics",
    description="Returns detailed statistics about the service including configuration, model information, and vector store status.",
    response_description="Service statistics and configuration"
)
async def get_service_stats():
    """
    Get service statistics and configuration.
    
    Returns information about:
    - LLM and embedding models in use
    - Document processing configuration
    - Vector store statistics
    - Available processing approaches
    
    Returns:
        ServiceStatsResponse: Comprehensive service statistics
    """
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


@app.post(
    "/evaluate/rag",
    response_model=EvaluationResponse,
    tags=["evaluation"],
    summary="Evaluate RAG response quality",
    description="""
    Evaluate the quality of a RAG response using LangSmith evaluation framework.
    
    **Metrics Evaluated:**
    
    1. **Answer Relevance** (0.0-1.0)
       - Measures how well the answer addresses the question
       - Higher = more directly relevant
    
    2. **Context Relevance** (0.0-1.0)
       - Measures how relevant retrieved chunks are to the question
       - Higher = better retrieval quality
    
    3. **Groundedness** (0.0-1.0)
       - Measures if answer claims are supported by context
       - Lower = potential hallucination
    
    4. **Overall Quality** (0.0-1.0)
       - Weighted average of all metrics
       - >0.8 = Excellent, >0.6 = Good, <0.4 = Needs improvement
    """,
    response_description="Evaluation metrics and quality scores"
)
async def evaluate_rag(request: EvaluationRequest):
    """
    Evaluate RAG response quality using LangSmith evaluation framework.
    
    Args:
        request: Evaluation request with question, answer, and context
        
    Returns:
        EvaluationResponse: Detailed quality metrics and statistics
        
    Example:
        ```json
        {
            "question": "What is AI?",
            "answer": "AI is artificial intelligence...",
            "context": ["AI is...", "Machine learning..."]
        }
        ```
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


@app.post(
    "/evaluate/query",
    tags=["evaluation"],
    summary="Ask question and evaluate quality",
    description="""
    Ask a question, get an AI-generated answer, and evaluate the response quality in one step.
    
    This is the **recommended** endpoint for quality evaluation. It combines:
    1. **Question Processing**: Retrieves relevant documents and generates answer
    2. **Quality Evaluation**: Assesses answer using LangSmith evaluation metrics
    3. **Recommendations**: Provides actionable improvement suggestions
    
    **Response includes:**
    - RAG answer with sources
    - Quality metrics (relevance, groundedness, etc.)
    - Quality assessment (Excellent/Good/Fair/Poor)
    - Improvement recommendations
    - Formatted evaluation summary
    
    **Use Cases:**
    - Quality monitoring in production
    - A/B testing different configurations
    - Debugging poor responses
    - Continuous improvement workflows
    """,
    response_description="Combined RAG response and evaluation results"
)
async def evaluate_query_json(request: QuestionRequest):
    """
    Ask a question, get an answer, and evaluate the response quality (JSON version).
    
    Args:
        request: Question request with question text and options
        
    Returns:
        dict: Combined results containing:
        - rag_response: The answer and sources
        - evaluation: Quality metrics and statistics
        - summary: Quality assessment and recommendations
        - summary_text: Human-readable evaluation summary
        
    Example Request:
    ```json
    {
            "question": "What skills does the candidate have?",
            "k": 5,
            "use_conversation_history": false,
            "use_llamaindex": true
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
