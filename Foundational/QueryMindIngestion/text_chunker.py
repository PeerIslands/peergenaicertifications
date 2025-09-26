"""
Text chunking functionality using LangChain with semantic chunking and recursive character splitting.
"""
from typing import List, Dict, Any, Optional
from langchain_experimental.text_splitter import SemanticChunker
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from config import settings


class TextChunker:
    """Handles text chunking using LangChain with semantic chunking and recursive character splitting."""
    
    def __init__(self, chunking_method: str, chunk_size: int, chunk_overlap: int):
        """
        Initialize text chunker with specified chunking method and parameters.
        
        Args:
            chunking_method: Either "semantic" or "recursive" for chunking method
            chunk_size: Size of chunks for recursive character splitting (default: 700)
            chunk_overlap: Overlap between chunks for recursive character splitting (default: 50)
        """
        self.chunking_method = chunking_method
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.semantic_threshold = settings.semantic_chunking_threshold
        self.chunk_separators = ["\n\n", "."]
        
        if chunking_method == "semantic":
            # Initialize embeddings for semantic chunking using Ollama
            try:
                self.embeddings = OllamaEmbeddings(
                    base_url=settings.ollama_base_url,
                    model=settings.embedding_model  # Use the same embedding model as configured
                )
            except Exception as e:
                raise Exception(f"Failed to initialize semantic embeddings: {str(e)}. Please ensure Ollama is running and the '{settings.embedding_model}' model is available.")
            
            # Initialize semantic text splitter
            self.text_splitter = SemanticChunker(
                embeddings=self.embeddings,
                breakpoint_threshold_amount=self.semantic_threshold,
                min_chunk_size=100
            )
        elif chunking_method == "recursive":
            # Initialize recursive character text splitter
            self.text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap,
                length_function=len,
                separators=self.chunk_separators
            )
            self.embeddings = None  # Not needed for recursive splitting
        else:
            raise ValueError(f"Invalid chunking method: {chunking_method}. Must be 'semantic' or 'recursive'.")
    
    def chunk_text(self, text: str, metadata: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Split text into chunks using the configured chunking method and return list of chunk dictionaries."""
        if not text.strip():
            return []
            
        # Split text into chunks using the configured method
        if self.chunking_method == "semantic":
            from langchain.schema import Document
            doc = Document(page_content=text, metadata=metadata or {})
            chunks = self.text_splitter.split_documents([doc])
            chunk_texts = [chunk.page_content for chunk in chunks]
        elif self.chunking_method == "recursive":
            chunk_texts = self.text_splitter.split_text(text)
        else:
            raise ValueError(f"Invalid chunking method: {self.chunking_method}")
        
        # Create chunk documents with metadata
        chunk_documents = []
        for i, chunk_text in enumerate(chunk_texts):
            chunk_doc = {
                "chunk_index": i,
                "chunk_text": chunk_text.strip(),
                "chunk_size": len(chunk_text),
                "metadata": metadata or {}
            }
            chunk_documents.append(chunk_doc)
            
        return chunk_documents
    
    def chunk_pdf_data(self, pdf_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Chunk PDF data and return list of chunk documents."""
        # Prepare metadata for chunks
        chunk_metadata = {
            "source_file": pdf_data["file_name"],
            "source_path": pdf_data["file_path"],
            "total_pages": pdf_data["total_pages"],
            "pdf_metadata": pdf_data["metadata"]
        }
        
        # Chunk the text content
        chunks = self.chunk_text(pdf_data["text_content"], chunk_metadata)
        
        return chunks
    
    def get_chunking_info(self) -> Dict[str, Any]:
        """Get information about the current chunking configuration."""
        info = {
            "chunking_method": self.chunking_method,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
        
        if self.chunking_method == "semantic":
            info.update({
                "semantic_threshold": self.semantic_threshold,
                "embedding_model": settings.embedding_model,
                "ollama_base_url": settings.ollama_base_url,
                "embeddings_available": self.embeddings is not None
            })
        elif self.chunking_method == "recursive":
            info.update({
                "separators": self.chunk_separators,
                "embeddings_available": False
            })
            
        return info
