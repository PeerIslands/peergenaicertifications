"""
Vector Store Repository - Handles vector search operations.

This repository manages vector embeddings and similarity search operations,
providing an abstraction layer over the vector database.
"""
import logging
from typing import List, Dict, Any, Optional
import pymongo
from pymongo import MongoClient

from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch as LlamaMongoVectorStore
from llama_index.core.storage.storage_context import StorageContext

from ..config.settings import settings

logger = logging.getLogger(__name__)


class VectorStoreRepository:
    """Repository for vector search operations."""
    
    def __init__(self, mongodb_client: Optional[MongoClient] = None):
        """
        Initialize vector store repository.
        
        Args:
            mongodb_client: MongoDB client instance (optional)
        """
        self.client = mongodb_client or MongoClient(settings.mongodb_uri)
        
        # Initialize embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        
        # LangChain vector store
        self.langchain_vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=settings.mongodb_uri,
            namespace=f"{settings.mongodb_database}.{settings.mongodb_collection}",
            embedding=self.embeddings,
            index_name=settings.vector_index_name,
            text_key="text",
            embedding_key="embedding"
        )
        
        # LlamaIndex vector store
        self.llamaindex_vector_store = LlamaMongoVectorStore(
            mongodb_client=self.client,
            db_name=settings.mongodb_database,
            collection_name=settings.mongodb_collection,
            index_name=settings.vector_index_name
        )
        
        logger.info("VectorStoreRepository initialized")
    
    def add_documents_langchain(self, documents: List[Any]) -> List[str]:
        """
        Add documents to vector store using LangChain.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            List of document IDs
        """
        try:
            doc_ids = self.langchain_vector_store.add_documents(documents)
            logger.info(f"Added {len(doc_ids)} documents to LangChain vector store")
            return doc_ids
        except Exception as e:
            logger.error(f"Failed to add documents to LangChain vector store: {str(e)}")
            raise
    
    def similarity_search_langchain(
        self,
        query: str,
        k: int = 5,
        filter_dict: Optional[Dict[str, Any]] = None
    ) -> List[Any]:
        """
        Perform similarity search using LangChain.
        
        Args:
            query: Search query
            k: Number of results to return
            filter_dict: Optional metadata filter
            
        Returns:
            List of similar documents
        """
        try:
            retriever = self.langchain_vector_store.as_retriever(
                search_kwargs={"k": k}
            )
            results = retriever.get_relevant_documents(query)
            logger.info(f"Found {len(results)} similar documents using LangChain")
            return results
        except Exception as e:
            logger.error(f"Similarity search failed (LangChain): {str(e)}")
            return []
    
    def get_llamaindex_storage_context(self) -> StorageContext:
        """
        Get storage context for LlamaIndex.
        
        Returns:
            StorageContext configured with MongoDB vector store
        """
        try:
            storage_context = StorageContext.from_defaults(
                vector_store=self.llamaindex_vector_store
            )
            logger.info("Created LlamaIndex storage context")
            return storage_context
        except Exception as e:
            logger.error(f"Failed to create storage context: {str(e)}")
            raise
    
    def verify_vector_index(self) -> bool:
        """
        Verify that the vector search index exists.
        
        Returns:
            True if index exists, False otherwise
        """
        try:
            db = self.client[settings.mongodb_database]
            collection = db[settings.mongodb_collection]
            indexes = list(collection.list_indexes())
            
            # Check if vector index exists
            for index in indexes:
                if index.get("name") == settings.vector_index_name:
                    logger.info(f"Vector index '{settings.vector_index_name}' exists")
                    return True
            
            logger.warning(f"Vector index '{settings.vector_index_name}' not found")
            return False
            
        except Exception as e:
            logger.error(f"Failed to verify vector index: {str(e)}")
            return False
    
    def get_vector_store_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store.
        
        Returns:
            Dictionary with vector store statistics
        """
        try:
            db = self.client[settings.mongodb_database]
            collection = db[settings.mongodb_collection]
            
            stats = {
                "type": "MongoDB Atlas Vector Search",
                "database": settings.mongodb_database,
                "collection": settings.mongodb_collection,
                "index_name": settings.vector_index_name,
                "embedding_model": settings.embedding_model,
                "document_count": collection.count_documents({}),
                "index_exists": self.verify_vector_index()
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get vector store stats: {str(e)}")
            return {"error": str(e)}
    
    def close(self):
        """Close connections."""
        try:
            self.client.close()
            logger.info("VectorStoreRepository connections closed")
        except Exception as e:
            logger.error(f"Error closing connections: {str(e)}")

