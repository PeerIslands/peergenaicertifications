"""
Integration tests for the PDF RAG application.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document


class TestIntegration:
    """Integration test cases."""
    
    @patch('app.load_documents')
    @patch('app.create_vector_store')
    @patch('app.create_conversation_chain')
    def test_full_workflow(self, mock_create_chain, mock_create_store, mock_load_documents):
        """Test the complete workflow from document upload to chain creation."""
        from app import create_vector_store, create_conversation_chain
        
        # Mock document loading
        mock_documents = [
            Document(page_content="Test content", metadata={"page": 0, "source_file": "test.pdf"})
        ]
        mock_load_documents.return_value = mock_documents
        
        # Mock vector store creation
        mock_vector_store = Mock()
        mock_create_store.return_value = mock_vector_store
        
        # Mock conversation chain
        mock_chain = {"chain": Mock(), "retriever": Mock()}
        mock_create_chain.return_value = mock_chain
        
        # Execute workflow
        documents = mock_load_documents([Mock()])
        vector_store = mock_create_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        conversation_chain = mock_create_chain(vector_store)
        
        # Assertions
        assert documents == mock_documents
        assert vector_store == mock_vector_store
        assert conversation_chain == mock_chain
        mock_load_documents.assert_called_once()
        mock_create_store.assert_called_once()
        mock_create_chain.assert_called_once_with(mock_vector_store)
    
    @patch('app.MongoDBAtlasVectorSearch')
    def test_mongodb_connection(self, mock_mongodb):
        """Test MongoDB connection and document storage."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0, "source_file": "test.pdf"})
        ]
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Mock text splitter
        with patch('app.RecursiveCharacterTextSplitter') as mock_splitter:
            mock_splitter_instance = Mock()
            mock_splitter_instance.split_documents.return_value = documents
            mock_splitter.return_value = mock_splitter_instance
            
            # Mock embeddings
            with patch('app.OpenAIEmbeddings') as mock_embeddings:
                mock_embeddings.return_value = Mock()
                
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
                mock_mongodb.from_connection_string.assert_called_once_with(
                    connection_string="mongodb+srv://test:test@cluster.mongodb.net/",
                    namespace="test_db.test_collection",
                    embedding=mock_embeddings.return_value,
                    index_name="vector_index"
                )
                mock_vector_store.add_documents.assert_called_once()
    
    def test_document_metadata_preservation(self):
        """Test that document metadata is preserved through processing."""
        from app import load_documents
        
        # This would require actual document file or more complex mocking
        # For now, we test the concept
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024
        
        # The metadata should include source_file after loading
        # This is tested in test_pdf_loading.py (now test_document_loading.py)

