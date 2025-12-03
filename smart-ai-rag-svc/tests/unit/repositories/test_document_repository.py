"""
Unit tests for DocumentRepository.
"""
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime

from src.repositories.document_repository import DocumentRepository


class TestDocumentRepository:
    """Test DocumentRepository class."""
    
    @pytest.fixture
    def repository(self, mock_mongodb_client):
        """Create DocumentRepository instance."""
        with patch('src.repositories.document_repository.MongoClient', return_value=mock_mongodb_client):
            repo = DocumentRepository(mock_mongodb_client)
            yield repo
    
    def test_insert_documents(self, repository, mock_mongodb_client):
        """Test inserting documents."""
        documents = [
            {"text": "Doc 1", "metadata": {"source": "test1.pdf"}},
            {"text": "Doc 2", "metadata": {"source": "test2.pdf"}}
        ]
        
        doc_ids = repository.insert_documents(documents)
        
        assert len(doc_ids) == 3  # Mocked to return 3 IDs
        assert all(isinstance(id, str) for id in doc_ids)
        # Verify created_at was added
        call_args = mock_mongodb_client[repository.db.name][repository.collection.name].insert_many.call_args
        inserted_docs = call_args[0][0]
        assert all('created_at' in doc for doc in inserted_docs)
    
    def test_find_document_by_id(self, repository):
        """Test finding document by ID."""
        # Use valid ObjectId format (24 hex characters)
        valid_id = "507f1f77bcf86cd799439011"
        doc = repository.find_document_by_id(valid_id)
        
        assert doc is not None
        assert "text" in doc
    
    def test_count_documents(self, repository, mock_mongodb_client):
        """Test counting documents."""
        count = repository.count_documents()
        
        assert count == 10
    
    def test_delete_document_by_id(self, repository):
        """Test deleting document by ID."""
        # Use valid ObjectId format (24 hex characters)
        valid_id = "507f1f77bcf86cd799439011"
        result = repository.delete_document_by_id(valid_id)
        
        assert result is True
    
    def test_get_collection_stats(self, repository):
        """Test getting collection statistics."""
        stats = repository.get_collection_stats()
        
        assert "document_count" in stats
        assert stats["document_count"] == 10
        assert "storage_size" in stats

