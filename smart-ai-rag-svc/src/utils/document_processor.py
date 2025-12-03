"""
Document Processing Utilities for PDF Loading and Text Chunking.

This module provides functionality for loading PDF documents and splitting them
into smaller chunks suitable for vector embedding and retrieval. It uses
LangChain's document loaders and text splitters for processing.

Classes:
    DocumentProcessor: Main class for PDF document processing and chunking.

Example:
    ```python
    processor = DocumentProcessor()
    documents = processor.process_pdf("document.pdf")
    stats = processor.get_document_stats(documents)
    ```
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from ..config.settings import settings

# Configure logging
logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Handles PDF document loading and text processing for RAG applications.
    
    This class provides methods to load PDF files, split them into chunks,
    and process multiple documents. It uses LangChain's RecursiveCharacterTextSplitter
    for intelligent text splitting that preserves semantic boundaries.
    
    Attributes:
        chunk_size (int): Maximum size of each text chunk in characters.
        chunk_overlap (int): Number of characters to overlap between chunks.
        text_splitter (RecursiveCharacterTextSplitter): Text splitter instance.
    
    Example:
        ```python
        processor = DocumentProcessor(chunk_size=1000, chunk_overlap=200)
        documents = processor.process_pdf("resume.pdf")
        ```
    """
    
    def __init__(self, chunk_size: Optional[int] = None, chunk_overlap: Optional[int] = None):
        """
        Initialize the document processor with chunking configuration.
        
        Args:
            chunk_size: Size of text chunks in characters. If None, uses value
                       from settings. Larger chunks preserve more context but
                       may be less precise for retrieval.
            chunk_overlap: Overlap between chunks in characters. If None, uses
                          value from settings. Overlap helps maintain context
                          across chunk boundaries.
        
        Raises:
            ValueError: If chunk_size or chunk_overlap are invalid (negative or
                       chunk_overlap >= chunk_size).
        
        Note:
            The text splitter uses a hierarchical approach:
            1. Split by double newlines (paragraphs)
            2. Split by single newlines (sentences)
            3. Split by spaces (words)
            4. Split by characters (if needed)
        """
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        
        # Validate chunk parameters
        if self.chunk_size <= 0:
            raise ValueError(f"chunk_size must be positive, got {self.chunk_size}")
        if self.chunk_overlap < 0:
            raise ValueError(f"chunk_overlap must be non-negative, got {self.chunk_overlap}")
        if self.chunk_overlap >= self.chunk_size:
            raise ValueError(
                f"chunk_overlap ({self.chunk_overlap}) must be less than "
                f"chunk_size ({self.chunk_size})"
            )
        
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        logger.info(
            f"DocumentProcessor initialized: chunk_size={self.chunk_size}, "
            f"chunk_overlap={self.chunk_overlap}"
        )
    
    def load_pdf(self, file_path: str) -> List[Document]:
        """
        Load a PDF file and extract text content from all pages.
        
        This method uses PyPDFLoader to extract text from each page of the PDF.
        Each page becomes a separate Document object with metadata including
        the source file path and page number.
        
        Args:
            file_path: Path to the PDF file. Can be absolute or relative.
            
        Returns:
            List of Document objects, one per page. Each Document contains:
            - page_content: Extracted text from the page
            - metadata: Dict with 'source' (file path) and 'page' (page number)
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist at the given path.
            ValueError: If the file is not a valid PDF.
            Exception: For other errors during PDF loading (corrupted file, etc.).
        
        Example:
            ```python
            documents = processor.load_pdf("resume.pdf")
            print(f"Loaded {len(documents)} pages")
            print(documents[0].page_content[:100])  # First 100 chars
            ```
        """
        if not os.path.exists(file_path):
            logger.error(f"PDF file not found: {file_path}")
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        if not file_path.lower().endswith('.pdf'):
            logger.warning(f"File {file_path} does not have .pdf extension")
        
        try:
            logger.info(f"Loading PDF file: {file_path}")
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            
            # Log statistics
            total_chars = sum(len(doc.page_content) for doc in documents)
            logger.info(
                f"Successfully loaded PDF: {len(documents)} pages, "
                f"{total_chars:,} total characters"
            )
            
            return documents
            
        except FileNotFoundError:
            raise
        except Exception as e:
            logger.error(
                f"Error loading PDF {file_path}: {str(e)}",
                exc_info=True
            )
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
    
    def get_document_stats(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Calculate and return statistics about processed documents.
        
        This method analyzes a list of documents and returns useful statistics
        including total count, character counts, and average lengths. Useful for
        monitoring and debugging document processing pipelines.
        
        Args:
            documents: List of Document objects to analyze. Can be empty.
            
        Returns:
            Dictionary containing:
            - total_documents (int): Number of documents
            - total_characters (int): Total characters across all documents
            - average_length (float): Average characters per document
            - chunk_size (int): Chunk size used for processing
            - chunk_overlap (int): Chunk overlap used for processing
        
        Example:
            ```python
            documents = processor.process_pdf("document.pdf")
            stats = processor.get_document_stats(documents)
            print(f"Processed {stats['total_documents']} chunks")
            print(f"Average length: {stats['average_length']} characters")
            ```
        """
        if not documents:
            logger.debug("No documents provided for statistics calculation")
            return {
                "total_documents": 0,
                "total_characters": 0,
                "average_length": 0,
                "chunk_size": self.chunk_size,
                "chunk_overlap": self.chunk_overlap
            }
        
        total_chars = sum(len(doc.page_content) for doc in documents)
        avg_length = total_chars / len(documents) if documents else 0
        
        stats = {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "average_length": round(avg_length, 2),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap
        }
        
        logger.debug(
            f"Document stats: {stats['total_documents']} docs, "
            f"{stats['total_characters']:,} chars, "
            f"avg {stats['average_length']:.1f} chars/doc"
        )
        
        return stats
