"""
MongoDB Vector Database Setup and Operations
"""
import os
from typing import List, Dict, Any
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
from azure_embeddings import HybridEmbeddingService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorMongoDB:
    """MongoDB Vector Database for storing document chunks with embeddings"""
    
    def __init__(self, connection_string: str = None, database_name: str = "rag_documents", use_azure_openai: bool = False):
        """
        Initialize MongoDB connection
        
        Args:
            connection_string: MongoDB connection string (defaults to localhost)
            database_name: Name of the database to use
            use_azure_openai: Whether to use Azure OpenAI for embeddings
        """
        self.connection_string = connection_string or "mongodb://localhost:27017/"
        self.database_name = database_name
        self.client = None
        self.database = None
        self.collection = None
        self.embedding_service = None
        self.use_azure_openai = use_azure_openai
        
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            self.client = MongoClient(self.connection_string)
            self.database = self.client[self.database_name]
            self.collection = self.database["document_chunks"]
            
            # Test connection
            self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {self.database_name}")
            
            # Initialize embedding service
            if self.use_azure_openai:
                self.embedding_service = HybridEmbeddingService(
                    use_azure=True,
                    endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                    api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                    api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                    deployment_name=os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002')
                )
                logger.info("Azure OpenAI embedding service loaded successfully")
            else:
                self.embedding_service = HybridEmbeddingService(use_azure=False)
                logger.info("Sentence transformer embedding service loaded successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    def create_indexes(self):
        """Create necessary indexes for efficient querying"""
        try:
            # Create text index for full-text search
            self.collection.create_index([("text", "text")])
            
            # Create index on document_id for filtering
            self.collection.create_index("document_id")
            
            # Create index on page_number for page-based queries
            self.collection.create_index("page_number")
            
            # Create index on chunk_index for ordering
            self.collection.create_index("chunk_index")
            
            logger.info("Database indexes created successfully")
            
        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for given text"""
        try:
            return self.embedding_service.generate_embedding(text)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            raise
    
    def insert_chunk(self, chunk_data: Dict[str, Any]) -> str:
        """
        Insert a single document chunk with embedding
        
        Args:
            chunk_data: Dictionary containing chunk information
            
        Returns:
            str: Inserted document ID
        """
        try:
            # Generate embedding for the text
            embedding = self.generate_embedding(chunk_data['text'])
            chunk_data['embedding'] = embedding
            
            # Insert document
            result = self.collection.insert_one(chunk_data)
            logger.info(f"Inserted chunk {chunk_data.get('chunk_index', 'unknown')} for document {chunk_data.get('document_id', 'unknown')}")
            return str(result.inserted_id)
            
        except Exception as e:
            logger.error(f"Failed to insert chunk: {e}")
            raise
    
    def insert_chunks_batch(self, chunks_data: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple document chunks in batch
        
        Args:
            chunks_data: List of dictionaries containing chunk information
            
        Returns:
            List[str]: List of inserted document IDs
        """
        try:
            # Generate embeddings for all chunks
            texts = [chunk['text'] for chunk in chunks_data]
            embeddings = self.embedding_service.generate_embeddings_batch(texts)
            
            # Add embeddings to chunk data
            for i, chunk_data in enumerate(chunks_data):
                chunk_data['embedding'] = embeddings[i]
            
            # Insert all documents
            result = self.collection.insert_many(chunks_data)
            logger.info(f"Inserted {len(result.inserted_ids)} chunks in batch")
            return [str(doc_id) for doc_id in result.inserted_ids]
            
        except Exception as e:
            logger.error(f"Failed to insert chunks batch: {e}")
            raise
    
    def search_similar(self, query_text: str, limit: int = 10, document_id: str = None) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using vector similarity
        
        Args:
            query_text: Text to search for
            limit: Maximum number of results to return
            document_id: Optional document ID to filter results
            
        Returns:
            List[Dict]: List of similar chunks
        """
        try:
            # Generate embedding for query
            query_embedding = self.generate_embedding(query_text)
            
            # Build aggregation pipeline for vector search
            pipeline = [
                {
                    "$vectorSearch": {
                        "index": "vector_index",  # This would need to be created separately
                        "path": "embedding",
                        "queryVector": query_embedding,
                        "numCandidates": limit * 10,
                        "limit": limit
                    }
                }
            ]
            
            # Add document filter if specified
            if document_id:
                pipeline.append({"$match": {"document_id": document_id}})
            
            # Execute search
            results = list(self.collection.aggregate(pipeline))
            
            # Remove embedding from results to reduce payload size
            for result in results:
                result.pop('embedding', None)
            
            logger.info(f"Found {len(results)} similar chunks for query")
            return results
            
        except Exception as e:
            logger.error(f"Vector search not available, falling back to text search: {e}")
            # Fallback to text search
            query = {"$text": {"$search": query_text}}
            if document_id:
                query["document_id"] = document_id
            
            results = list(self.collection.find(query).limit(limit))
            for result in results:
                result.pop('embedding', None)
            
            return results
    
    def get_document_chunks(self, document_id: str) -> List[Dict[str, Any]]:
        """Get all chunks for a specific document"""
        try:
            chunks = list(self.collection.find({"document_id": document_id}).sort("chunk_index", 1))
            for chunk in chunks:
                chunk.pop('embedding', None)
            return chunks
        except Exception as e:
            logger.error(f"Failed to get document chunks: {e}")
            raise
    
    def get_document_stats(self) -> Dict[str, Any]:
        """Get statistics about stored documents"""
        try:
            stats = {
                "total_chunks": self.collection.count_documents({}),
                "unique_documents": len(self.collection.distinct("document_id")),
                "total_pages": len(self.collection.distinct("page_number"))
            }
            return stats
        except Exception as e:
            logger.error(f"Failed to get document stats: {e}")
            raise
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")
