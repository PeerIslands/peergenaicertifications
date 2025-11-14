"""
Unit tests for configuration and session state handling.
"""
import pytest
from unittest.mock import Mock, patch


class TestConfiguration:
    """Test cases for configuration handling."""
    
    def test_default_database_name(self):
        """Test that default database name is set correctly."""
        # This tests the initialization logic
        # Since we can't easily test Streamlit session state without running the app,
        # we test the logic indirectly through the function that uses it
        from app import create_vector_store
        from langchain_core.documents import Document
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        # Test that function accepts default database name
        # The actual default is set in session state initialization
        with patch('app.MongoDBAtlasVectorSearch') as mock_mongodb, \
             patch('app.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('app.OpenAIEmbeddings') as mock_embeddings:
            
            mock_splitter_instance = Mock()
            mock_splitter_instance.split_documents.return_value = documents
            mock_splitter.return_value = mock_splitter_instance
            
            mock_embeddings.return_value = Mock()
            
            mock_vector_store = Mock()
            mock_mongodb.from_connection_string.return_value = mock_vector_store
            
            # Use default database name
            result = create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "document_rag",  # Default database name
                "documents",
                "vector_index"
            )
            
            # Verify it was called with correct namespace
            mock_mongodb.from_connection_string.assert_called_once()
            call_args = mock_mongodb.from_connection_string.call_args
            assert "document_rag.documents" in call_args.kwargs['namespace']
    
    def test_custom_database_name(self):
        """Test that custom database name is used correctly."""
        from app import create_vector_store
        from langchain_core.documents import Document
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        with patch('app.MongoDBAtlasVectorSearch') as mock_mongodb, \
             patch('app.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('app.OpenAIEmbeddings') as mock_embeddings:
            
            mock_splitter_instance = Mock()
            mock_splitter_instance.split_documents.return_value = documents
            mock_splitter.return_value = mock_splitter_instance
            
            mock_embeddings.return_value = Mock()
            
            mock_vector_store = Mock()
            mock_mongodb.from_connection_string.return_value = mock_vector_store
            
            # Use custom database name
            custom_db_name = "my_custom_db"
            result = create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                custom_db_name,
                "documents",
                "vector_index"
            )
            
            # Verify it was called with custom namespace
            call_args = mock_mongodb.from_connection_string.call_args
            assert f"{custom_db_name}.documents" in call_args.kwargs['namespace']
    
    def test_collection_name_usage(self):
        """Test that collection name is used correctly in namespace."""
        from app import create_vector_store
        from langchain_core.documents import Document
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        with patch('app.MongoDBAtlasVectorSearch') as mock_mongodb, \
             patch('app.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('app.OpenAIEmbeddings') as mock_embeddings:
            
            mock_splitter_instance = Mock()
            mock_splitter_instance.split_documents.return_value = documents
            mock_splitter.return_value = mock_splitter_instance
            
            mock_embeddings.return_value = Mock()
            
            mock_vector_store = Mock()
            mock_mongodb.from_connection_string.return_value = mock_vector_store
            
            custom_collection = "my_custom_collection"
            result = create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "test_db",
                custom_collection,
                "vector_index"
            )
            
            # Verify it was called with custom collection in namespace
            call_args = mock_mongodb.from_connection_string.call_args
            assert f"test_db.{custom_collection}" in call_args.kwargs['namespace']
    
    def test_index_name_usage(self):
        """Test that index name is passed correctly."""
        from app import create_vector_store
        from langchain_core.documents import Document
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        with patch('app.MongoDBAtlasVectorSearch') as mock_mongodb, \
             patch('app.RecursiveCharacterTextSplitter') as mock_splitter, \
             patch('app.OpenAIEmbeddings') as mock_embeddings:
            
            mock_splitter_instance = Mock()
            mock_splitter_instance.split_documents.return_value = documents
            mock_splitter.return_value = mock_splitter_instance
            
            mock_embeddings.return_value = Mock()
            
            mock_vector_store = Mock()
            mock_mongodb.from_connection_string.return_value = mock_vector_store
            
            custom_index = "my_custom_index"
            result = create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "test_db",
                "test_collection",
                custom_index
            )
            
            # Verify it was called with custom index name
            call_args = mock_mongodb.from_connection_string.call_args
            assert call_args.kwargs['index_name'] == custom_index

