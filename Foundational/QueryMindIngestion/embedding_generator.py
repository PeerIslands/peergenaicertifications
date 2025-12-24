"""
Embedding generation using Ollama and LangChain.
"""
from typing import List, Dict, Any
from langchain_community.embeddings import OllamaEmbeddings
from config import settings


class EmbeddingGenerator:
    """Handles embedding generation using Ollama."""
    
    def __init__(self, base_url: str = None, model_name: str = None):
        """Initialize embedding generator."""
        self.base_url = base_url or settings.ollama_base_url
        self.model_name = model_name or settings.embedding_model
        
        # Initialize Ollama embeddings
        self.embeddings = OllamaEmbeddings(
            base_url=self.base_url,
            model=self.model_name
        )
    
    def generate_embedding(self, text: str) -> List[float]:
        """Generate embedding for a single text."""
        try:
            embedding = self.embeddings.embed_query(text)
            return embedding
        except Exception as e:
            raise Exception(f"Error generating embedding: {str(e)}")
    
    def generate_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
        try:
            embeddings = self.embeddings.embed_documents(texts)
            return embeddings
        except Exception as e:
            raise Exception(f"Error generating batch embeddings: {str(e)}")
    
    def test_connection(self) -> bool:
        """Test connection to Ollama."""
        try:
            # Test with a simple embedding
            test_embedding = self.generate_embedding("test")
            if test_embedding and len(test_embedding) > 0:
                print(f"Successfully connected to Ollama at {self.base_url}")
                print(f"Using model: {self.model_name}")
                print(f"Embedding dimension: {len(test_embedding)}")
                return True
            else:
                print("Failed to generate test embedding")
                return False
        except Exception as e:
            print(f"Failed to connect to Ollama: {str(e)}")
            return False
