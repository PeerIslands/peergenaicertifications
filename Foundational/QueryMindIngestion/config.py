"""
Configuration settings for PDF ingestion tool.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # PDF folder path
    pdf_folder_path: str = Field(default="./pdfs", description="Path to folder containing PDF files")
    
    # MongoDB settings
    mongodb_uri: str = Field(..., description="MongoDB connection URI (required, set via MONGODB_URI environment variable)")
    mongodb_database: str = Field(default="query-mind", description="MongoDB database name")
    mongodb_collection: str = Field(default="knowledge-base", description="MongoDB collection name")
    
    # Ollama settings
    ollama_base_url: str = Field(default="http://localhost:11434", description="Ollama base URL")
    embedding_model: str = Field(default="embeddinggemma", description="Ollama embedding model name")
    
    # Semantic chunking settings
    semantic_chunking_threshold: float = Field(default=0.7, description="Threshold for semantic similarity in chunking (0.35 recommended for academic papers)")
    
    # Text chunking settings (for compatibility)
    chunk_size: Optional[int] = Field(default=None, description="Chunk size for text splitting")
    chunk_overlap: Optional[int] = Field(default=None, description="Chunk overlap for text splitting")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
