"""
MongoDB client for storing PDF chunks and embeddings.
"""
from typing import List, Dict, Any, Optional
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from bson import ObjectId
from config import settings


class MongoDBClient:
    """Handles MongoDB operations for PDF chunks storage."""
    
    def __init__(self, uri: str = None, database_name: str = None, collection_name: str = None):
        """Initialize MongoDB client."""
        self.uri = uri or settings.mongodb_uri
        self.database_name = database_name or settings.mongodb_database
        self.collection_name = collection_name or settings.mongodb_collection
        
        # Initialize MongoDB client
        self.client: MongoClient = MongoClient(self.uri)
        self.database: Database = self.client[self.database_name]
        self.collection: Collection = self.database[self.collection_name]
        
    def test_connection(self) -> bool:
        """Test MongoDB connection."""
        try:
            # Test connection by pinging the server
            self.client.admin.command('ping')
            print(f"Successfully connected to MongoDB at {self.uri}")
            return True
        except Exception as e:
            print(f"Failed to connect to MongoDB: {str(e)}")
            return False
    
    def create_indexes(self):
        """Create useful indexes for the collection."""
        try:
            # Create index on source_file for faster queries
            self.collection.create_index("metadata.source_file")
            
            # Create index on chunk_index for ordering
            self.collection.create_index("chunk_index")
            
            # Create text index for full-text search
            self.collection.create_index([("chunk_text", "text")])
            
            print("MongoDB indexes created successfully")
        except Exception as e:
            print(f"Error creating indexes: {str(e)}")
    
    def insert_chunk(self, chunk_data: Dict[str, Any]) -> str:
        """Insert a single chunk into MongoDB."""
        try:
            result = self.collection.insert_one(chunk_data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting chunk: {str(e)}")
    
    def insert_chunks(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """Insert multiple chunks into MongoDB."""
        if not chunks:
            return []
            
        try:
            result = self.collection.insert_many(chunks)
            return [str(id) for id in result.inserted_ids]
        except Exception as e:
            raise Exception(f"Error inserting chunks: {str(e)}")
    
    def update_chunk_embedding(self, chunk_id: str, embedding: List[float]) -> bool:
        """Update a chunk with its embedding vector."""
        try:
            result = self.collection.update_one(
                {"_id": ObjectId(chunk_id)},
                {"$set": {"embedding": embedding}}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error updating chunk embedding: {str(e)}")
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a chunk by its ID."""
        try:
            return self.collection.find_one({"_id": ObjectId(chunk_id)})
        except Exception as e:
            raise Exception(f"Error retrieving chunk: {str(e)}")
    
    def get_chunks_by_file(self, source_file: str) -> List[Dict[str, Any]]:
        """Retrieve all chunks for a specific source file."""
        try:
            cursor = self.collection.find({"metadata.source_file": source_file})
            return list(cursor)
        except Exception as e:
            raise Exception(f"Error retrieving chunks for file {source_file}: {str(e)}")
    
    def get_all_chunks(self) -> List[Dict[str, Any]]:
        """Retrieve all chunks from the collection."""
        try:
            cursor = self.collection.find()
            return list(cursor)
        except Exception as e:
            raise Exception(f"Error retrieving all chunks: {str(e)}")
    
    def delete_chunks_by_file(self, source_file: str) -> int:
        """Delete all chunks for a specific source file."""
        try:
            result = self.collection.delete_many({"metadata.source_file": source_file})
            return result.deleted_count
        except Exception as e:
            raise Exception(f"Error deleting chunks for file {source_file}: {str(e)}")
    
    def clear_all_documents(self) -> int:
        """Delete all documents from the collection."""
        try:
            result = self.collection.delete_many({})
            deleted_count = result.deleted_count
            print(f"Cleared {deleted_count} documents from MongoDB collection")
            return deleted_count
        except Exception as e:
            raise Exception(f"Error clearing all documents: {str(e)}")
    
    def close_connection(self):
        """Close MongoDB connection."""
        self.client.close()
