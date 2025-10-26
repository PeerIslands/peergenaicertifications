import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
from datetime import datetime
import numpy as np
from config import settings
from services.embeddings import EmbeddingService

class VectorStore:
    def __init__(self):
        self.client = AsyncIOMotorClient(settings.MONGODB_URI)
        self.db = self.client[settings.DATABASE_NAME]
        self.collection = self.db.document_chunks
        self.embedding_service = EmbeddingService()
    
    async def create_index(self):
        """Create vector index for embeddings"""
        try:
            # Create vector index for cosine similarity
            await self.collection.create_index(
                [("embedding", "2dsphere")],
                name="vector_index"
            )
            print("Vector index created successfully")
        except Exception as e:
            print(f"Index creation failed (may already exist): {e}")
    
    async def store_chunks(self, processed_files: List[Dict]) -> int:
        """Store document chunks with embeddings in MongoDB"""
        total_chunks = 0
        
        for file_data in processed_files:
            doc_id = file_data["doc_id"]
            file_name = file_data["file_name"]
            chunks = file_data["chunks"]
            
            # Generate embeddings for all chunks
            texts = [chunk["content"] for chunk in chunks]
            embeddings = self.embedding_service.generate_embeddings(texts)
            
            # Prepare documents for insertion
            documents = []
            for i, chunk in enumerate(chunks):
                doc = {
                    "doc_id": doc_id,
                    "file_name": file_name,
                    "chunk_id": chunk["chunk_id"],
                    "content": chunk["content"],
                    "embedding": embeddings[i],
                    "metadata": chunk["metadata"],
                    "chunk_index": chunk["chunk_index"],
                    "created_at": datetime.now(),
                }
                documents.append(doc)
            
            # Insert documents
            if documents:
                await self.collection.insert_many(documents)
                total_chunks += len(documents)
        
        return total_chunks
    
    async def search_similar_chunks(self, query: str, top_k: int = None) -> List[Dict]:
        """Search for similar chunks using vector similarity"""
        if top_k is None:
            top_k = settings.TOP_K_CHUNKS
        
        # Generate query embedding
        query_embedding = self.embedding_service.generate_embedding(query)
        
        # For now, we'll use a simple approach since MongoDB Atlas vector search
        # requires a specific setup. We'll implement a basic cosine similarity search
        all_chunks = await self.collection.find({}).to_list(length=None)
        
        if not all_chunks:
            return []
        
        # Calculate cosine similarities
        similarities = []
        for chunk in all_chunks:
            if "embedding" in chunk:
                similarity = self._cosine_similarity(query_embedding, chunk["embedding"])
                similarities.append((similarity, chunk))
        
        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[0], reverse=True)
        return [chunk for _, chunk in similarities[:top_k]]
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0
        
        return dot_product / (norm1 * norm2)
    
    async def clear_all_chunks(self):
        """Clear all stored chunks"""
        result = await self.collection.delete_many({})
        return result.deleted_count
    
    async def get_chunk_count(self) -> int:
        """Get total number of stored chunks"""
        return await self.collection.count_documents({})
    
    async def get_document_count(self) -> int:
        """Get number of unique documents"""
        pipeline = [
            {"$group": {"_id": "$doc_id"}},
            {"$count": "total"}
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0
