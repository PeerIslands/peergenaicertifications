"""
LlamaIndex-based document processing utilities for enhanced PDF loading and indexing.
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

# LlamaIndex imports - using current, non-deprecated methods
from llama_index.core import Document, VectorStoreIndex, Settings
from llama_index.core.node_parser import SentenceWindowNodeParser
from llama_index.readers.file import PDFReader
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch
from llama_index.core.storage.storage_context import StorageContext

from ..config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LlamaIndexProcessor:
    """Enhanced document processor using LlamaIndex for better ingestion and indexing."""
    
    def __init__(self):
        """Initialize the LlamaIndex processor with OpenAI and MongoDB."""
        
        # Configure LlamaIndex global settings - non-deprecated approach
        # Use actual model names from environment variables
        Settings.llm = OpenAI(
            model=settings.llm_model,  # This will use gpt-3.5-turbo from your .env
            temperature=settings.temperature,
            max_tokens=settings.max_tokens,
            api_key=settings.openai_api_key
        )
        
        # Use the actual embedding model from environment variables
        Settings.embed_model = OpenAIEmbedding(
            model=settings.embedding_model,  # This will use text-embedding-ada-002 from your .env
            api_key=settings.openai_api_key
        )
        
        # Initialize Sentence Window Node Parser for better context retrieval
        # Note: SentenceWindowNodeParser splits by sentences, NOT by chunk_size/chunk_overlap
        # It creates small sentence nodes and uses window_size for context expansion
        self.node_parser = SentenceWindowNodeParser.from_defaults(
            window_size=settings.sentence_window_size,  # Number of sentences before/after (default: 3)
            window_metadata_key="window",
            original_text_metadata_key="original_text"
        )
        
        logger.info(f"Sentence Window Node Parser initialized (window_size={settings.sentence_window_size})")
        
        # Initialize PDF reader
        self.pdf_reader = PDFReader()
        
        logger.info("LlamaIndex processor initialized successfully")
    
    def load_pdf(self, file_path: str, original_filename: Optional[str] = None) -> List[Document]:
        """
        Load a PDF file using LlamaIndex PDFReader.
        
        Args:
            file_path: Path to the PDF file
            original_filename: Original filename to store in metadata (optional)
            
        Returns:
            List of LlamaIndex Document objects
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
            Exception: If there's an error loading the PDF
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")
        
        try:
            logger.info(f"Loading PDF with LlamaIndex: {file_path}")
            documents = self.pdf_reader.load_data(file=Path(file_path))
            
            # Add metadata to documents with original filename if provided
            actual_filename = original_filename or os.path.basename(file_path)
            for doc in documents:
                doc.metadata["source"] = file_path
                doc.metadata["file_name"] = actual_filename
                doc.metadata["original_filename"] = actual_filename
                if original_filename:
                    doc.metadata["temp_file_path"] = file_path
            
            logger.info(f"Successfully loaded {len(documents)} documents from PDF")
            return documents
            
        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {str(e)}")
            raise
    
    def load_multiple_pdfs(self, directory_path: str) -> List[Document]:
        """
        Load all PDF files from a directory using LlamaIndex.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            List of LlamaIndex Document objects from all PDFs
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
    
    def create_nodes(self, documents: List[Document]) -> List:
        """
        Parse documents into nodes (chunks) using LlamaIndex.
        
        Args:
            documents: List of LlamaIndex Document objects
            
        Returns:
            List of nodes ready for indexing
        """
        if not documents:
            logger.warning("No documents provided for node creation")
            return []
        
        try:
            logger.info(f"Creating nodes from {len(documents)} documents...")
            nodes = self.node_parser.get_nodes_from_documents(documents)
            logger.info(f"Created {len(nodes)} nodes from {len(documents)} documents")
            return nodes
            
        except Exception as e:
            logger.error(f"Error creating nodes: {str(e)}")
            raise
    
    def create_index(self, documents: List[Document], storage_context: Optional[StorageContext] = None) -> VectorStoreIndex:
        """
        Create a VectorStoreIndex from documents using current methods.
        
        Args:
            documents: List of LlamaIndex Document objects
            storage_context: Optional storage context for vector store
            
        Returns:
            VectorStoreIndex ready for querying
        """
        try:
            logger.info(f"Creating vector index from {len(documents)} documents...")
            
            if storage_context:
                index = VectorStoreIndex.from_documents(
                    documents, 
                    storage_context=storage_context,
                    transformations=[self.node_parser]  # Using transformations instead of deprecated node_parser
                )
            else:
                index = VectorStoreIndex.from_documents(
                    documents,
                    transformations=[self.node_parser]  # Using transformations instead of deprecated node_parser
                )
            
            logger.info("Vector index created successfully")
            return index
            
        except Exception as e:
            logger.error(f"Error creating index: {str(e)}")
            raise
    
    def process_pdf(self, file_path: str, original_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete pipeline: load PDF, create nodes, and prepare for indexing.
        
        Args:
            file_path: Path to the PDF file
            original_filename: Original filename to store in metadata (optional)
            
        Returns:
            Dictionary containing processed documents, nodes, and metadata
        """
        try:
            # Load documents with original filename
            documents = self.load_pdf(file_path, original_filename)
            
            # Create nodes
            nodes = self.create_nodes(documents)
            
            # Calculate statistics
            stats = self.get_processing_stats(documents, nodes)
            
            return {
                "success": True,
                "documents": documents,
                "nodes": nodes,
                "stats": stats,
                "message": f"Successfully processed PDF: {original_filename or os.path.basename(file_path)}"
            }
            
        except Exception as e:
            logger.error(f"Error processing PDF {file_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process PDF: {original_filename or os.path.basename(file_path)}"
            }
    
    def process_pdf_directory(self, directory_path: str) -> Dict[str, Any]:
        """
        Complete pipeline: load all PDFs from directory, create nodes, and prepare for indexing.
        
        Args:
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary containing processed documents, nodes, and metadata
        """
        try:
            # Load documents
            documents = self.load_multiple_pdfs(directory_path)
            
            if not documents:
                return {
                    "success": False,
                    "message": "No documents found to process",
                    "stats": {"total_documents": 0, "total_nodes": 0}
                }
            
            # Create nodes
            nodes = self.create_nodes(documents)
            
            # Calculate statistics
            stats = self.get_processing_stats(documents, nodes)
            
            return {
                "success": True,
                "documents": documents,
                "nodes": nodes,
                "stats": stats,
                "message": f"Successfully processed {len(documents)} documents from directory"
            }
            
        except Exception as e:
            logger.error(f"Error processing directory {directory_path}: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "message": f"Failed to process directory: {directory_path}"
            }
    
    def get_processing_stats(self, documents: List[Document], nodes: List = None) -> Dict[str, Any]:
        """
        Get statistics about the processed documents and nodes.
        
        Args:
            documents: List of Document objects
            nodes: List of node objects (optional)
            
        Returns:
            Dictionary containing processing statistics
        """
        if not documents:
            return {
                "total_documents": 0,
                "total_nodes": 0,
                "total_characters": 0,
                "average_doc_length": 0,
                "average_node_length": 0
            }
        
        # Document statistics
        total_chars = sum(len(doc.text) for doc in documents)
        avg_doc_length = total_chars / len(documents) if documents else 0
        
        # Node statistics
        node_stats = {}
        if nodes:
            node_chars = sum(len(node.text) for node in nodes)
            avg_node_length = node_chars / len(nodes) if nodes else 0
            node_stats = {
                "total_nodes": len(nodes),
                "average_node_length": round(avg_node_length, 2)
            }
        
        return {
            "total_documents": len(documents),
            "total_characters": total_chars,
            "average_doc_length": round(avg_doc_length, 2),
            "chunk_size": settings.chunk_size,
            "chunk_overlap": settings.chunk_overlap,
            **node_stats
        }
    
    def create_storage_context(self, mongodb_client) -> StorageContext:
        """
        Create a storage context with MongoDB vector store using current methods.
        
        Args:
            mongodb_client: MongoDB client instance
            
        Returns:
            StorageContext configured with MongoDB vector store
        """
        try:
            # Create vector store with current methods
            vector_store = MongoDBAtlasVectorSearch(
                mongodb_client=mongodb_client,
                db_name=settings.mongodb_database,
                collection_name=settings.mongodb_collection,
                index_name=settings.vector_index_name
            )
            
            storage_context = StorageContext.from_defaults(vector_store=vector_store)
            logger.info("Storage context created with MongoDB vector store")
            return storage_context
            
        except Exception as e:
            logger.error(f"Error creating storage context: {str(e)}")
            raise
