"""
Extended unit tests for vector store creation functionality.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document


class TestVectorStoreExtended:
    """Extended test cases for create_vector_store function."""
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_text_splitter_parameters(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that text splitter is configured with correct parameters."""
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
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Verify splitter was called with correct parameters
        mock_splitter.assert_called_once_with(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len
        )
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_namespace_format(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that namespace is formatted correctly as db.collection."""
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
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        db_name = "my_database"
        collection_name = "my_collection"
        
        # Execute
        create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            db_name,
            collection_name,
            "vector_index"
        )
        
        # Verify namespace format
        call_args = mock_mongodb.from_connection_string.call_args
        assert call_args.kwargs['namespace'] == f"{db_name}.{collection_name}"
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_embeddings_initialization(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that embeddings are initialized correctly."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content", metadata={"page": 0})
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_splitter_instance.split_documents.return_value = documents
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings_instance = Mock()
        mock_embeddings.return_value = mock_embeddings_instance
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Verify embeddings were initialized
        mock_embeddings.assert_called_once()
        # Verify embeddings were passed to MongoDB
        call_args = mock_mongodb.from_connection_string.call_args
        assert call_args.kwargs['embedding'] == mock_embeddings_instance
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_chunks_added_to_vector_store(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that chunks are correctly added to vector store."""
        from app import create_vector_store
        
        documents = [
            Document(page_content="Test content 1", metadata={"page": 0}),
            Document(page_content="Test content 2", metadata={"page": 1})
        ]
        
        # Mock text splitter to return chunks
        mock_splitter_instance = Mock()
        mock_chunks = [
            Document(page_content="Chunk 1", metadata={"page": 0}),
            Document(page_content="Chunk 2", metadata={"page": 0}),
            Document(page_content="Chunk 3", metadata={"page": 1})
        ]
        mock_splitter_instance.split_documents.return_value = mock_chunks
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Verify chunks were added
        mock_vector_store.add_documents.assert_called_once()
        added_chunks = mock_vector_store.add_documents.call_args[0][0]
        assert len(added_chunks) == 3
        assert added_chunks == mock_chunks
    
    @patch('app.OpenAIEmbeddings')
    @patch('app.MongoDBAtlasVectorSearch')
    @patch('app.RecursiveCharacterTextSplitter')
    def test_metadata_preserved_in_chunks(self, mock_splitter, mock_mongodb, mock_embeddings):
        """Test that metadata is preserved when documents are chunked."""
        from app import create_vector_store
        
        documents = [
            Document(
                page_content="Test content",
                metadata={"page": 0, "source_file": "test.pdf"}
            )
        ]
        
        # Mock text splitter
        mock_splitter_instance = Mock()
        mock_chunks = [
            Document(
                page_content="Chunk 1",
                metadata={"page": 0, "source_file": "test.pdf"}
            )
        ]
        mock_splitter_instance.split_documents.return_value = mock_chunks
        mock_splitter.return_value = mock_splitter_instance
        
        # Mock embeddings
        mock_embeddings.return_value = Mock()
        
        # Mock MongoDB vector store
        mock_vector_store = Mock()
        mock_mongodb.from_connection_string.return_value = mock_vector_store
        
        # Execute
        create_vector_store(
            documents,
            "mongodb+srv://test:test@cluster.mongodb.net/",
            "test_db",
            "test_collection",
            "vector_index"
        )
        
        # Verify metadata is preserved
        added_chunks = mock_vector_store.add_documents.call_args[0][0]
        assert added_chunks[0].metadata['source_file'] == "test.pdf"
        assert added_chunks[0].metadata['page'] == 0

