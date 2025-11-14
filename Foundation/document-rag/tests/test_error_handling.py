"""
Unit tests for error handling and edge cases.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document


class TestErrorHandling:
    """Test cases for error handling scenarios."""
    
    def test_create_vector_store_empty_documents(self):
        """Test vector store creation with empty document list."""
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
    def test_create_vector_store_connection_error(self, mock_splitter, mock_mongodb, mock_embeddings):
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
        
        # Mock MongoDB to raise connection error
        mock_mongodb.from_connection_string.side_effect = Exception("Connection failed")
        
        # Execute and assert exception is raised
        with pytest.raises(Exception, match="Connection failed"):
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
    def test_create_vector_store_add_documents_error(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test handling of errors when adding documents to vector store."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_chunks = [
            Document(page_content="Chunk 1", metadata={"page": 0})
        ]
        mock_splitter_instance.split_documents.return_value = mock_chunks
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_vector_store.add_documents.side_effect = Exception("Failed to add documents")
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute and assert exception is raised
        with pytest.raises(Exception, match="Failed to add documents"):
            create_vector_store(
                documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "test_db",
                "test_collection",
                "vector_index"
            )
    
    @patch('app.ChatOpenAI')
    def test_create_conversation_chain_no_vector_store(self, mock_chat_openai):
        """Test conversation chain creation with None vector store."""
        from app import create_conversation_chain
        
        # This should handle None gracefully or raise appropriate error
        # Depending on implementation, adjust test accordingly
        with pytest.raises((AttributeError, TypeError)):
            create_conversation_chain(None)
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_conversation_chain_retriever_error(self, mock_prompt_template, mock_chat_openai):
        """Test handling of retriever creation errors."""
        from app import create_conversation_chain
        
        # Mock vector store that fails to create retriever
        mock_vector_store = Mock()
        mock_vector_store.as_retriever.side_effect = Exception("Retriever creation failed")
        
        # Execute and assert exception is raised
        with pytest.raises(Exception, match="Retriever creation failed"):
            create_conversation_chain(mock_vector_store)
    
    def test_workflow_with_loading_error(self):
        """Test workflow when document loading fails (empty documents)."""
        from app import create_vector_store
        
        # Try to create vector store with empty documents (simulating loading failure)
        result = create_vector_store(
            [],  # Empty documents list
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Assertions - should return None for empty documents
        assert result is None
    
    @patch('app.load_documents')
    @patch('app.create_vector_store')
    def test_workflow_with_vector_store_error(self, mock_create_store, mock_load_documents):
        """Test workflow when vector store creation fails."""
        from app import create_vector_store
        
        # Mock document loading
        mock_documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        mock_load_documents.return_value = mock_documents
        
        # Mock vector store creation to fail
        mock_create_store.side_effect = Exception("Vector store creation failed")
        
        # Execute and assert exception is raised
        with pytest.raises(Exception, match="Vector store creation failed"):
            create_vector_store(
                mock_documents,
                "mongodb+srv://test:test@cluster.mongodb.net/",
                "test_db",
                "test_collection",
                "vector_index"
            )

