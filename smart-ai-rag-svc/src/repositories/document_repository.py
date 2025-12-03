"""
Document Repository - Handles All Document Database Operations.

This repository provides an abstraction layer for MongoDB document operations,
implementing the Repository pattern to separate data access logic from business
logic. All database operations go through this repository.

Classes:
    DocumentRepository: Main repository class for document CRUD operations.

Example:
    ```python
    repo = DocumentRepository(mongodb_client)
    doc_ids = repo.insert_documents([{"text": "..."}])
    doc = repo.find_document_by_id(doc_ids[0])
    ```
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from ..config.settings import settings

logger = logging.getLogger(__name__)


class DocumentRepository:
    """Repository for document-related database operations."""
    
    def __init__(self, mongodb_client: Optional[MongoClient] = None):
        """
        Initialize document repository.
        
        Args:
            mongodb_client: MongoDB client instance (optional, creates new if not provided)
        """
        self.client = mongodb_client or MongoClient(settings.mongodb_uri)
        self.db: Database = self.client[settings.mongodb_database]
        self.collection: Collection = self.db[settings.mongodb_collection]
        logger.info(f"DocumentRepository initialized for collection: {settings.mongodb_collection}")
    
    def insert_documents(self, documents: List[Dict[str, Any]]) -> List[str]:
        """
        Insert multiple documents into MongoDB collection.
        
        This method adds documents to the MongoDB collection with automatic
        timestamp tracking. Each document gets created_at and updated_at fields
        if not already present.
        
        Args:
            documents: List of document dictionaries to insert. Each dict should
                      contain the document data. Metadata like timestamps are
                      automatically added.
            
        Returns:
            List of inserted document IDs as strings. IDs are MongoDB ObjectIds
            converted to strings for easier handling.
            
        Raises:
            pymongo.errors.PyMongoError: If MongoDB operation fails (connection
                                        issues, write errors, etc.).
            Exception: For other unexpected errors during insertion.
        
        Example:
            ```python
            docs = [
                {"text": "Document 1", "metadata": {"source": "doc1.pdf"}},
                {"text": "Document 2", "metadata": {"source": "doc2.pdf"}}
            ]
            doc_ids = repo.insert_documents(docs)
            print(f"Inserted {len(doc_ids)} documents")
            ```
        
        Note:
            This is a bulk insert operation. For large batches, consider
            using insert_many with ordered=False for better performance.
        """
        try:
            if not documents:
                logger.warning("Attempted to insert empty document list")
                return []
            
            # Add timestamps to documents
            now = datetime.utcnow()
            for doc in documents:
                if 'created_at' not in doc:
                    doc['created_at'] = now
                if 'updated_at' not in doc:
                    doc['updated_at'] = now
            
            logger.debug(f"Inserting {len(documents)} documents into collection")
            result = self.collection.insert_many(documents)
            doc_ids = [str(obj_id) for obj_id in result.inserted_ids]
            
            logger.info(
                f"Successfully inserted {len(doc_ids)} documents into MongoDB "
                f"collection '{self.collection.name}'"
            )
            return doc_ids
            
        except Exception as e:
            logger.error(
                f"Failed to insert {len(documents)} documents: {str(e)}",
                exc_info=True
            )
            raise
    
    def find_document_by_id(self, document_id: str) -> Optional[Dict[str, Any]]:
        """
        Find a document by its ID.
        
        Args:
            document_id: Document ID to search for
            
        Returns:
            Document dict if found, None otherwise
        """
        try:
            from bson import ObjectId
            doc = self.collection.find_one({"_id": ObjectId(document_id)})
            return doc
        except Exception as e:
            logger.error(f"Failed to find document {document_id}: {str(e)}")
            return None
    
    def find_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Find documents matching metadata criteria.
        
        Args:
            metadata_filter: Dictionary of metadata key-value pairs to filter by
            
        Returns:
            List of matching documents
        """
        try:
            # Build query for metadata fields
            query = {f"metadata.{key}": value for key, value in metadata_filter.items()}
            documents = list(self.collection.find(query))
            logger.info(f"Found {len(documents)} documents matching metadata filter")
            return documents
        except Exception as e:
            logger.error(f"Failed to find documents by metadata: {str(e)}")
            return []
    
    def count_documents(self, filter_dict: Optional[Dict[str, Any]] = None) -> int:
        """
        Count documents in collection.
        
        Args:
            filter_dict: Optional filter criteria
            
        Returns:
            Number of documents
        """
        try:
            count = self.collection.count_documents(filter_dict or {})
            return count
        except Exception as e:
            logger.error(f"Failed to count documents: {str(e)}")
            return 0
    
    def delete_document_by_id(self, document_id: str) -> bool:
        """
        Delete a document by ID.
        
        Args:
            document_id: Document ID to delete
            
        Returns:
            True if deleted, False otherwise
        """
        try:
            from bson import ObjectId
            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            if result.deleted_count > 0:
                logger.info(f"Deleted document: {document_id}")
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete document {document_id}: {str(e)}")
            return False
    
    def delete_documents_by_metadata(self, metadata_filter: Dict[str, Any]) -> int:
        """
        Delete documents matching metadata criteria.
        
        Args:
            metadata_filter: Metadata filter criteria
            
        Returns:
            Number of documents deleted
        """
        try:
            query = {f"metadata.{key}": value for key, value in metadata_filter.items()}
            result = self.collection.delete_many(query)
            logger.info(f"Deleted {result.deleted_count} documents")
            return result.deleted_count
        except Exception as e:
            logger.error(f"Failed to delete documents: {str(e)}")
            return 0
    
    def update_document(self, document_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update a document.
        
        Args:
            document_id: Document ID to update
            update_data: Data to update
            
        Returns:
            True if updated, False otherwise
        """
        try:
            from bson import ObjectId
            update_data['updated_at'] = datetime.utcnow()
            result = self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Failed to update document {document_id}: {str(e)}")
            return False
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the document collection.
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            stats = {
                "document_count": self.count_documents(),
                "database": settings.mongodb_database,
                "collection": settings.mongodb_collection,
                "indexes": list(self.collection.list_indexes()),
            }
            
            # Get storage size
            db_stats = self.db.command("collStats", settings.mongodb_collection)
            stats["storage_size"] = db_stats.get("size", 0)
            stats["avg_document_size"] = db_stats.get("avgObjSize", 0)
            
            return stats
        except Exception as e:
            logger.error(f"Failed to get collection stats: {str(e)}")
            return {
                "error": str(e),
                "document_count": 0
            }
    
    def close(self):
        """Close MongoDB connection."""
        try:
            self.client.close()
            logger.info("DocumentRepository connection closed")
        except Exception as e:
            logger.error(f"Error closing connection: {str(e)}")

