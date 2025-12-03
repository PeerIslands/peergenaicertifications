"""
Pydantic models for API request/response schemas.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """
    Request model for document upload by file path.
    
    Provide either file_path for a single PDF or directory_path for multiple PDFs.
    """
    file_path: Optional[str] = Field(
        None,
        description="Path to a single PDF file to upload and index",
        example="/path/to/resume.pdf"
    )
    directory_path: Optional[str] = Field(
        None,
        description="Path to directory containing multiple PDF files to process",
        example="/path/to/documents/"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/document.pdf"
            },
            "examples": [
                {
                    "file_path": "/path/to/resume.pdf",
                    "summary": "Upload single PDF file"
                },
                {
                    "directory_path": "/path/to/documents/",
                    "summary": "Upload all PDFs from directory"
                }
            ]
        }


class QuestionRequest(BaseModel):
    """
    Request model for asking questions to the RAG service.
    
    The service will retrieve relevant document chunks and generate an answer
    using the configured LLM model.
    """
    question: str = Field(
        ...,
        description="The question to ask about the indexed documents",
        min_length=1,
        max_length=10000,
        example="What is the main topic of this document?"
    )
    k: Optional[int] = Field(
        5,
        description="Number of relevant document chunks to retrieve for context",
        ge=1,
        le=100,
        example=5
    )
    use_conversation_history: bool = Field(
        False,
        description="Whether to include previous conversation context in the answer",
        example=False
    )
    use_llamaindex: bool = Field(
        True,
        description="Whether to use LlamaIndex (recommended) or LangChain processor",
        example=True
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of the document?",
                "k": 5,
                "use_conversation_history": False,
                "use_llamaindex": True
            },
            "examples": [
                {
                    "question": "What skills does the candidate have?",
                    "k": 5,
                    "use_conversation_history": False,
                    "use_llamaindex": True,
                    "summary": "Simple question without history"
                },
                {
                    "question": "Tell me more about that",
                    "k": 3,
                    "use_conversation_history": True,
                    "use_llamaindex": True,
                    "summary": "Follow-up question with conversation context"
                }
            ]
        }


class SourceInfo(BaseModel):
    """
    Model for source document information.
    
    Represents a document chunk that was used to generate the answer.
    """
    chunk_id: int = Field(
        ...,
        description="Unique identifier for this document chunk",
        example=0
    )
    content_preview: str = Field(
        ...,
        description="Preview of the chunk content (first 200 characters)",
        example="Artificial intelligence (AI) is transforming healthcare by enabling..."
    )
    metadata: Dict[str, Any] = Field(
        ...,
        description="Metadata about the source document (filename, page number, etc.)",
        example={"source": "resume.pdf", "page": 1, "file_name": "resume.pdf"}
    )


class QuestionResponse(BaseModel):
    """
    Response model for question answers.
    
    Contains the AI-generated answer along with source information and metadata.
    """
    answer: str = Field(
        ...,
        description="The AI-generated answer to the question",
        example="The document discusses artificial intelligence and machine learning..."
    )
    sources: List[SourceInfo] = Field(
        ...,
        description="List of source document chunks used to generate the answer"
    )
    num_sources: int = Field(
        ...,
        description="Number of source chunks used",
        example=5
    )
    processing_time: float = Field(
        ...,
        description="Time taken to process the question in seconds",
        example=1.23
    )
    timestamp: str = Field(
        ...,
        description="ISO timestamp of when the response was generated",
        example="2024-12-01T10:30:00"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if processing failed",
        example=None
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "answer": "The document discusses artificial intelligence and machine learning applications in healthcare.",
                "sources": [
                    {
                        "chunk_id": 0,
                        "content_preview": "Artificial intelligence (AI) is transforming healthcare...",
                        "metadata": {"source": "document.pdf", "page": 1}
                    }
                ],
                "num_sources": 5,
                "processing_time": 1.23,
                "timestamp": "2024-12-01T10:30:00",
                "error": None
            }
        }


class DocumentUploadResponse(BaseModel):
    """
    Response model for document upload operations.
    
    Contains information about the upload and indexing process.
    """
    success: bool = Field(
        ...,
        description="Whether the upload and indexing succeeded",
        example=True
    )
    message: str = Field(
        ...,
        description="Status message describing the result",
        example="Successfully indexed 1 documents with 15 nodes using LlamaIndex"
    )
    document_ids: Optional[List[str]] = Field(
        None,
        description="List of document IDs in the database (for LangChain)",
        example=["507f1f77bcf86cd799439011"]
    )
    document_stats: Optional[Dict[str, Any]] = Field(
        None,
        description="Statistics about processed documents",
        example={
            "total_documents": 1,
            "total_nodes": 15,
            "total_characters": 5000,
            "average_doc_length": 5000
        }
    )
    collection_stats: Optional[Dict[str, Any]] = Field(
        None,
        description="Statistics about the MongoDB collection",
        example={"document_count": 10, "storage_size": 1024000}
    )
    original_filename: Optional[str] = Field(
        None,
        description="Original filename of the uploaded file",
        example="resume.pdf"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Successfully indexed 1 documents with 15 nodes using LlamaIndex",
                "document_stats": {
                    "total_documents": 1,
                    "total_nodes": 15,
                    "total_characters": 5000
                },
                "original_filename": "resume.pdf"
            }
        }


class ConversationMessage(BaseModel):
    """Model for conversation history messages."""
    type: str  # "human" or "ai"
    content: str
    timestamp: str


class ServiceStatsResponse(BaseModel):
    """Response model for service statistics."""
    llm_model: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
    top_k_results: int
    similarity_threshold: float
    conversation_history_length: int
    vector_store_stats: Dict[str, Any]


class HealthCheckResponse(BaseModel):
    """Response model for health check."""
    status: str
    timestamp: str
    version: str = "1.0.0"


class EvaluationRequest(BaseModel):
    """
    Request model for RAG evaluation.
    
    Used to evaluate the quality of a RAG response after it has been generated.
    """
    question: str = Field(
        ...,
        description="The original question that was asked",
        example="What is artificial intelligence?"
    )
    answer: str = Field(
        ...,
        description="The generated answer to evaluate",
        example="Artificial intelligence (AI) is the simulation of human intelligence..."
    )
    context: List[str] = Field(
        ...,
        description="List of context chunks used to generate the answer",
        example=["AI is a branch of computer science...", "Machine learning is a subset of AI..."]
    )
    source_info: Optional[List[Dict[str, Any]]] = Field(
        None,
        description="Optional metadata about the source documents",
        example=[{"source": "document.pdf", "page": 1}]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is AI?",
                "answer": "AI is artificial intelligence...",
                "context": ["AI is...", "Machine learning..."]
            }
        }


class EvaluationMetrics(BaseModel):
    """
    Model for RAG evaluation metrics.
    
    All metrics are scores between 0.0 and 1.0, where higher is better.
    """
    answer_relevance: float = Field(
        ...,
        description="How relevant is the answer to the question? (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.85
    )
    context_relevance: float = Field(
        ...,
        description="How relevant are the retrieved context chunks? (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.80
    )
    groundedness: float = Field(
        ...,
        description="Is the answer grounded in the context? (0.0-1.0). Low scores indicate hallucination.",
        ge=0.0,
        le=1.0,
        example=0.90
    )
    overall_quality: float = Field(
        ...,
        description="Weighted average of all metrics (0.0-1.0)",
        ge=0.0,
        le=1.0,
        example=0.85
    )


class EvaluationResponse(BaseModel):
    """
    Response model for RAG evaluation.
    
    Contains comprehensive quality metrics and statistics.
    """
    question: str = Field(..., description="The evaluated question")
    answer: str = Field(..., description="The evaluated answer")
    metrics: EvaluationMetrics = Field(..., description="Quality metrics scores")
    context_stats: Dict[str, Any] = Field(
        ...,
        description="Statistics about the context chunks",
        example={
            "num_chunks": 5,
            "total_chars": 2500,
            "avg_chunk_length": 500
        }
    )
    evaluation_time: float = Field(
        ...,
        description="Time taken to perform evaluation in seconds",
        example=2.5
    )
    timestamp: str = Field(..., description="ISO timestamp of evaluation")
    error: Optional[str] = Field(None, description="Error message if evaluation failed")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is AI?",
                "answer": "AI is artificial intelligence...",
                "metrics": {
                    "answer_relevance": 0.85,
                    "context_relevance": 0.80,
                    "groundedness": 0.90,
                    "overall_quality": 0.85
                },
                "context_stats": {
                    "num_chunks": 5,
                    "total_chars": 2500
                },
                "evaluation_time": 2.5,
                "timestamp": "2024-12-01T10:30:00",
                "error": None
            }
        }
