"""
Unit tests for VectorStoreRepository.
"""
import pytest
from unittest.mock import MagicMock, patch

from src.repositories.vector_store_repository import VectorStoreRepository


class TestVectorStoreRepository:
    """Test VectorStoreRepository class."""
    
    @pytest.fixture
    def repository(self, mock_mongodb_client, mock_settings):
        """Create VectorStoreRepository instance."""
        with patch('src.repositories.vector_store_repository.MongoClient', return_value=mock_mongodb_client), \
             patch('src.repositories.vector_store_repository.OpenAIEmbeddings'), \
             patch('src.repositories.vector_store_repository.MongoDBAtlasVectorSearch'), \
             patch('src.repositories.vector_store_repository.LlamaMongoVectorStore'):
            repo = VectorStoreRepository(mock_mongodb_client)
            yield repo
    
    def test_initialization(self, repository):
        """Test repository initialization."""
        assert repository.client is not None
        assert repository.embeddings is not None
        assert repository.langchain_vector_store is not None
        assert repository.llamaindex_vector_store is not None
    
    def test_add_documents_langchain(self, repository, sample_documents):
        """Test adding documents using LangChain."""
        repository.langchain_vector_store.add_documents = MagicMock(
            return_value=["id1", "id2"]
        )
        
        doc_ids = repository.add_documents_langchain(sample_documents)
        
        assert len(doc_ids) == 2
        assert repository.langchain_vector_store.add_documents.called
    
    def test_similarity_search_langchain(self, repository):
        """Test similarity search using LangChain."""
        repository.langchain_vector_store.as_retriever = MagicMock()
        mock_retriever = MagicMock()
        mock_retriever.get_relevant_documents.return_value = ["doc1", "doc2"]
        repository.langchain_vector_store.as_retriever.return_value = mock_retriever
        
        results = repository.similarity_search_langchain("test query", k=5)
        
        assert len(results) == 2
    
    def test_verify_vector_index(self, repository):
        """Test vector index verification."""
        result = repository.verify_vector_index()
        
        assert isinstance(result, bool)
    
    def test_get_vector_store_stats(self, repository):
        """Test getting vector store statistics."""
        stats = repository.get_vector_store_stats()
        
        assert "type" in stats
        assert stats["type"] == "MongoDB Atlas Vector Search"
        assert "document_count" in stats

