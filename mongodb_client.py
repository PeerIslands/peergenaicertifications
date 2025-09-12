import certifi
import pymongo
from pymongo import MongoClient
from typing import List, Dict, Any
import numpy as np
from datetime import datetime
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME

class MongoDBClient:
    def __init__(self):
        try:
            self.client = MongoClient(MONGODB_URI,tlsCAFile=certifi.where())
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db[MONGODB_COLLECTION_NAME]
            
            # Create index for vector search (if using MongoDB Atlas Vector Search)
            # For basic similarity search, we'll use cosine similarity calculation
            self._ensure_indexes()
            
        except Exception as e:
            raise Exception(f"Error connecting to MongoDB: {str(e)}")
    
    def _ensure_indexes(self):
        """Create necessary indexes"""
        try:
            # Create index on filename for faster queries
            self.collection.create_index("filename")
            self.collection.create_index("timestamp")
        except Exception as e:
            print(f"Warning: Could not create indexes: {str(e)}")
    
    def store_document(self, document_data: Dict[str, Any]) -> str:
        """Store processed document in MongoDB"""
        try:
            # Prepare document for storage
            doc = {
                'filename': document_data['filename'],
                'text': document_data['text'],
                'chunks': [],
                'timestamp': datetime.now(),
                'num_chunks': document_data['num_chunks']
            }
            
            # Store each chunk with its embedding
            for i, (chunk, embedding) in enumerate(zip(document_data['chunks'], document_data['embeddings'])):
                chunk_doc = {
                    'chunk_id': i,
                    'text': chunk,
                    'embedding': embedding
                }
                doc['chunks'].append(chunk_doc)
            
            # Insert document
            result = self.collection.insert_one(doc)
            return str(result.inserted_id)
            
        except Exception as e:
            raise Exception(f"Error storing document in MongoDB: {str(e)}")
    
    def get_all_documents(self) -> List[Dict[str, Any]]:
        """Retrieve all documents metadata"""
        try:
            documents = []
            cursor = self.collection.find({}, {'filename': 1, 'timestamp': 1, 'num_chunks': 1})
            for doc in cursor:
                documents.append({
                    'id': str(doc['_id']),
                    'filename': doc['filename'],
                    'timestamp': doc['timestamp'],
                    'num_chunks': doc['num_chunks']
                })
            return documents
        except Exception as e:
            raise Exception(f"Error retrieving documents: {str(e)}")
    
    def cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm_vec1 = np.linalg.norm(vec1)
        norm_vec2 = np.linalg.norm(vec2)
        
        if norm_vec1 == 0 or norm_vec2 == 0:
            return 0
        
        return dot_product / (norm_vec1 * norm_vec2)
    
    def similarity_search(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Perform similarity search using cosine similarity"""
        try:
            results = []
            
            # Get all documents with chunks
            cursor = self.collection.find({})
            
            for doc in cursor:
                for chunk in doc['chunks']:
                    similarity = self.cosine_similarity(query_embedding, chunk['embedding'])
                    
                    results.append({
                        'document_id': str(doc['_id']),
                        'filename': doc['filename'],
                        'chunk_id': chunk['chunk_id'],
                        'text': chunk['text'],
                        'similarity': similarity
                    })
            
            # Sort by similarity and return top k
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:top_k]
            
        except Exception as e:
            raise Exception(f"Error performing similarity search: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """Delete a document by ID"""
        try:
            result = self.collection.delete_one({'_id': pymongo.ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error deleting document: {str(e)}")
    
    def clear_all_documents(self) -> int:
        """Clear all documents from the collection"""
        try:
            result = self.collection.delete_many({})
            return result.deleted_count
        except Exception as e:
            raise Exception(f"Error clearing documents: {str(e)}")
    
    def close_connection(self):
        """Close MongoDB connection"""
        try:
            self.client.close()
        except Exception as e:
            print(f"Warning: Error closing MongoDB connection: {str(e)}")
