"""
Document processing utilities for PDF loading and text chunking.
"""
import os
from typing import List, Optional
from pathlib import Path
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Handles PDF document loading and text processing."""
    
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """
        Initialize the document processor.
        
        Args:
            chunk_size: Size of text chunks (defaults to settings value)
            chunk_overlap: Overlap between chunks (defaults to settings value)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load a PDF file and extract text content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of Document objects containing the extracted text
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If there's an error loading the PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            logger.info(f"Loading PDF: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            logger.info(f"Successfully loaded {len(documents)} pages from PDF")
            return documents
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise
    
    def load_multiple_pdfs(self, directory_path: str) -> List[Document]:
        """
        Load all PDF files from a directory.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            List of Document objects from all PDFs
        """
        if not os.path.exists(directory_path):
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        all_documents = []
        pdf_files = list(Path(directory_path).glob("*.pdf"))
        
        if not pdf_files:
            logger.warning(f"No PDF files found in directory: {directory_path}")
            return all_documents
        
        for pdf_file in pdf_files:
            try:
                documents = self.load_pdf(str(pdf_file))
                all_documents.extend(documents)
            except Exception as e:
                logger.error(f"Failed to load {pdf_file}: {str(e)}")
                continue
        
        logger.info(f"Loaded total of {len(all_documents)} documents from {len(pdf_files)} PDF files")
        return all_documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """
        Split documents into smaller chunks for better retrieval.
        
        Args:
            documents: List of Document objects to chunk
            
        Returns:
            List of chunked Document objects
        """
        if not documents:
            logger.warning("No documents provided for chunking")
            return []
        
        try:
            logger.info(f"Chunking {len(documents)} documents...")
            chunked_docs = self.text_splitter.split_documents(documents)
            logger.info(f"Created {len(chunked_docs)} chunks from {len(documents)} documents")
            return chunked_docs
        except Exception as e:
            logger.error(f"Error chunking documents: {str(e)}")
            raise
    
    def process_pdf(self, file_path: str) -> List[Document]:
        """
        Complete pipeline: load PDF and chunk the content.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            List of chunked Document objects ready for embedding
        """
        documents = self.load_pdf(file_path)
        return self.chunk_documents(documents)
    
    def process_pdf_directory(self, directory_path: str) -> List[Document]:
        """
        Complete pipeline: load all PDFs from directory and chunk the content.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            List of chunked Document objects ready for embedding
        """
        documents = self.load_multiple_pdfs(directory_path)
        return self.chunk_documents(documents)
    
    def get_document_stats(self, documents: List[Document]) -> dict:
        """
        Get statistics about the processed documents.
        
        Args:
            documents: List of Document objects
            
        Returns:
            Dictionary containing document statistics
        """
        if not documents:
            return {"total_documents": 0, "total_characters": 0, "average_length": 0}
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_length = total_chars / len(documents) if documents else 0
        
        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "average_length": round(avg_length, 2),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
