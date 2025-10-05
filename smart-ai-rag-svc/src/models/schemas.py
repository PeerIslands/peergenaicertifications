"""
Pydantic models for API request/response schemas.
"""
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DocumentUploadRequest(BaseModel):
    """Request model for document upload."""
    file_path: Optional[str] = Field(None, description="Path to a single PDF file")
    directory_path: Optional[str] = Field(None, description="Path to directory containing PDF files")
    
    class Config:
        json_schema_extra = {
            "example": {
                "file_path": "/path/to/document.pdf"
            }
        }


class QuestionRequest(BaseModel):
    """Request model for asking questions."""
    question: str = Field(..., description="The question to ask")
    k: Optional[int] = Field(5, description="Number of relevant documents to retrieve")
    use_conversation_history: bool = Field(False, description="Whether to use conversation history")
    use_llamaindex: bool = Field(True, description="Whether to use LlamaIndex (True) or LangChain (False)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "question": "What is the main topic of the document?",
                "k": 5,
                "use_conversation_history": False,
                "use_llamaindex": True
            }
        }


class SourceInfo(BaseModel):
    """Model for source document information."""
    chunk_id: int
    content_preview: str
    metadata: Dict[str, Any]


class QuestionResponse(BaseModel):
    """Response model for question answers."""
    answer: str
    sources: List[SourceInfo]
    num_sources: int
    processing_time: float
    timestamp: str
    error: Optional[str] = None


class DocumentUploadResponse(BaseModel):
    """Response model for document upload."""
    success: bool
    message: str
    document_ids: Optional[List[str]] = None
    document_stats: Optional[Dict[str, Any]] = None
    collection_stats: Optional[Dict[str, Any]] = None
    original_filename: Optional[str] = None


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
    """Request model for RAG evaluation."""
    question: str
    answer: str
    context: List[str]
    source_info: Optional[List[Dict[str, Any]]] = None


class EvaluationMetrics(BaseModel):
    """Model for evaluation metrics."""
    answer_relevance: float
    context_relevance: float
    groundedness: float
    overall_quality: float


class EvaluationResponse(BaseModel):
    """Response model for RAG evaluation."""
    question: str
    answer: str
    metrics: EvaluationMetrics
    context_stats: Dict[str, Any]
    evaluation_time: float
    timestamp: str
    error: Optional[str] = None
