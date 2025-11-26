"""
Unit tests for vector store creation functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document


class TestVectorStoreCreation:
    """Test cases for create_vector_store function."""
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_create_vector_store_success(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test successful vector store creation."""
        from app import create_vector_store
        
        # Mock documents
        documents = [
            Document(page_content="Test content 1", metadata={"page": 0, "source_file": "test.pdf"}),
            Document(page_content="Test content 2", metadata={"page": 1, "source_file": "test.pdf"})
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_chunks = [
            Document(page_content="Chunk 1", metadata={"page": 0, "source_file": "test.pdf"}),
            Document(page_content="Chunk 2", metadata={"page": 1, "source_file": "test.pdf"})
        ]
        mock_splitter_instance.split_documents.return_value = mock_chunks
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        result = create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Assertions
        assert result is not None
        assert result == mock_vector_store
        mock_mongodb.from_connection_string.assert_called_once()
        mock_vector_store.add_documents.assert_called_once()
        mock_splitter_instance.split_documents.assert_called_once_with(documents)
    
    def test_create_vector_store_no_documents(self):
        """Test vector store creation with no documents."""
        from app import create_vector_store
        
        result = create_vector_store(
            [],
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        assert result is None
    
    def test_create_vector_store_no_mongodb_uri(self):
        """Test vector store creation without MongoDB URI."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        result = create_vector_store(
            documents,
            "",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        assert result is None
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_create_vector_store_mongodb_error(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test handling of MongoDB connection errors."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_documents.return_value = documents
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock MongoDB to raise exception
        mock_mongodb.from_connection_string.side_effect = Exception("Connection error")
        
        # Execute and assert exception is raised
        with pytest.raises(Exception):
            create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "test_db",
                "test_collection",
                "vector_index"
            )
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_create_vector_store_chunking(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that documents are properly chunked."""
        from app import create_vector_store
        
        # Create a long document that should be split
        long_content = " ".join(["word"] * 2000)  # ~10KB of text
        documents = [
            Document(page_content=long_content, metadata={"page": 0, "source_file": "test.pdf"})
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_chunks = [
            Document(page_content="Chunk 1", metadata={"page": 0, "source_file": "test.pdf"}),
            Document(page_content="Chunk 2", metadata={"page": 0, "source_file": "test.pdf"})
        ]
        mock_splitter_instance.split_documents.return_value = mock_chunks
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        result = create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Assertions
        assert result is not None
        # Verify splitter was called with correct parameters
        mock_splitter.assert_called_once()
        # Verify chunks were added to vector store
        assert mock_vector_store.add_documents.call_count == 1
        added_chunks = mock_vector_store.add_documents.call_args[0][0]
        assert len(added_chunks) == 2

