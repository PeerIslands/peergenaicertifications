import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import List, Dict
import numpy as np
from pathlib import Path
import tempfile
import os

from services.embeddings import EmbeddingService
from services.vector_store import VectorStore
from services.file_processor import FileProcessor
from services.rag_pipeline import RAGPipeline
from services.conversation_memory import ConversationMemory
from models.chat_request import ChatRequest, ChatResponse
from models.pdf_metadata import PDFMetadata, DocumentResponse


class TestEmbeddingService:
    """Test cases for EmbeddingService"""
    
    @pytest.fixture
    def embedding_service(self):
        with patch('services.embeddings.SentenceTransformer') as mock_model:
            mock_model.return_value.encode.return_value = np.array([[0.1, 0.2, 0.3]])
            return EmbeddingService()
    
    def test_init(self, embedding_service):
        """Test EmbeddingService initialization"""
        assert embedding_service.embedding_dimension == 384
        assert embedding_service.model is not None
    
    def test_generate_embedding(self, embedding_service):
        """Test single embedding generation"""
        text = "test text"
        embedding = embedding_service.generate_embedding(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 3  # Mock returns 3D vector
        assert all(isinstance(x, float) for x in embedding)
    
    def test_generate_embeddings(self, embedding_service):
        """Test multiple embeddings generation"""
        with patch.object(embedding_service.model, 'encode') as mock_encode:
            mock_encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6], [0.7, 0.8, 0.9]])
            
            texts = ["text1", "text2", "text3"]
            embeddings = embedding_service.generate_embeddings(texts)
            
            assert isinstance(embeddings, list)
            assert len(embeddings) == 3
            assert all(isinstance(emb, list) for emb in embeddings)
    
    def test_get_embedding_dimension(self, embedding_service):
        """Test getting embedding dimension"""
        dimension = embedding_service.get_embedding_dimension()
        assert dimension == 384


class TestVectorStore:
    """Test cases for VectorStore"""
    
    @pytest.fixture
    def vector_store(self):
        with patch('services.vector_store.AsyncIOMotorClient') as mock_client:
            mock_db = AsyncMock()
            mock_collection = AsyncMock()
            mock_client.return_value.__getitem__.return_value = mock_db
            mock_db.__getitem__.return_value = mock_collection
            
            # Create mock cursor for find operations
            mock_cursor = AsyncMock()
            mock_cursor.to_list = AsyncMock()
            mock_collection.find.return_value = mock_cursor
            
            # Create mock cursor for aggregate operations
            mock_agg_cursor = AsyncMock()
            mock_agg_cursor.to_list = AsyncMock()
            mock_collection.aggregate.return_value = mock_agg_cursor
            
            with patch('services.vector_store.EmbeddingService') as mock_embedding:
                mock_embedding.return_value.generate_embeddings.return_value = [[0.1, 0.2, 0.3]]
                mock_embedding.return_value.generate_embedding.return_value = [0.1, 0.2, 0.3]
                
                return VectorStore()
    
    @pytest.mark.asyncio
    async def test_create_index(self, vector_store):
        """Test vector index creation"""
        await vector_store.create_index()
        vector_store.collection.create_index.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_store_chunks(self, vector_store):
        """Test storing document chunks"""
        processed_files = [{
            "doc_id": "test_doc_id",
            "file_name": "test.pdf",
            "chunks": [
                {
                    "chunk_id": "chunk_1",
                    "content": "test content",
                    "metadata": {"page": 1},
                    "chunk_index": 0
                }
            ]
        }]
        
        vector_store.collection.insert_many = AsyncMock()
        
        total_chunks = await vector_store.store_chunks(processed_files)
        
        assert total_chunks == 1
        vector_store.collection.insert_many.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_clear_all_chunks(self, vector_store):
        """Test clearing all chunks"""
        vector_store.collection.delete_many = AsyncMock()
        vector_store.collection.delete_many.return_value.deleted_count = 5
        
        deleted_count = await vector_store.clear_all_chunks()
        
        assert deleted_count == 5
        vector_store.collection.delete_many.assert_called_once_with({})
    
    @pytest.mark.asyncio
    async def test_get_chunk_count(self, vector_store):
        """Test getting chunk count"""
        vector_store.collection.count_documents = AsyncMock(return_value=10)
        
        count = await vector_store.get_chunk_count()
        
        assert count == 10
    
    def test_cosine_similarity(self, vector_store):
        """Test cosine similarity calculation"""
        vec1 = [1, 0, 0]
        vec2 = [1, 0, 0]
        
        similarity = vector_store._cosine_similarity(vec1, vec2)
        
        assert similarity == 1.0  # Identical vectors should have similarity 1
    
    def test_cosine_similarity_orthogonal(self, vector_store):
        """Test cosine similarity with orthogonal vectors"""
        vec1 = [1, 0, 0]
        vec2 = [0, 1, 0]
        
        similarity = vector_store._cosine_similarity(vec1, vec2)
        
        assert similarity == 0.0  # Orthogonal vectors should have similarity 0


class TestFileProcessor:
    """Test cases for FileProcessor"""
    
    @pytest.fixture
    def file_processor(self):
        with patch('services.file_processor.RecursiveCharacterTextSplitter') as mock_splitter:
            mock_splitter.return_value.split_documents.return_value = [
                Mock(page_content="chunk 1", metadata={"page": 1}),
                Mock(page_content="chunk 2", metadata={"page": 2})
            ]
            return FileProcessor()
    
    def test_get_pdf_files(self, file_processor):
        """Test getting PDF files from directory"""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.glob') as mock_glob:
                mock_files = [Path("test1.pdf"), Path("test2.pdf")]
                mock_glob.return_value = mock_files
                
                pdf_files = file_processor.get_pdf_files()
                
                assert len(pdf_files) == 2
                assert all(f.suffix == '.pdf' for f in pdf_files)
    
    def test_get_pdf_files_no_directory(self, file_processor):
        """Test getting PDF files when directory doesn't exist"""
        with patch('pathlib.Path.exists', return_value=False):
            pdf_files = file_processor.get_pdf_files()
            
            assert pdf_files == []
    
    def test_process_pdf_file(self, file_processor):
        """Test processing a single PDF file"""
        with patch('services.file_processor.PyPDFLoader') as mock_loader:
            mock_docs = [Mock(page_content="test content", metadata={"page": 1})]
            mock_loader.return_value.load.return_value = mock_docs
            
            with patch('pathlib.Path.stat') as mock_stat:
                mock_stat.return_value.st_size = 1024
                
                result = file_processor.process_pdf_file(Path("test.pdf"))
                
                assert result["file_name"] == "test.pdf"
                assert result["file_size"] == 1024
                assert result["chunk_count"] == 2  # Mock returns 2 chunks
                assert len(result["chunks"]) == 2
    
    def test_process_pdf_file_error(self, file_processor):
        """Test processing PDF file with error"""
        with patch('services.file_processor.PyPDFLoader', side_effect=Exception("Load error")):
            result = file_processor.process_pdf_file(Path("error.pdf"))
            
            assert result["file_name"] == "error.pdf"
            assert result["file_size"] == 0
            assert result["chunk_count"] == 0
            assert result["chunks"] == []
    
    def test_process_all_files(self, file_processor):
        """Test processing all files"""
        with patch.object(file_processor, 'get_pdf_files') as mock_get_files:
            mock_files = [Path("test1.pdf"), Path("test2.pdf")]
            mock_get_files.return_value = mock_files
            
            with patch.object(file_processor, 'process_pdf_file') as mock_process:
                mock_process.return_value = {
                    "doc_id": "test_id",
                    "file_name": "test.pdf",
                    "file_size": 1024,
                    "chunks": [],
                    "chunk_count": 2
                }
                
                results = file_processor.process_all_files()
                
                assert len(results) == 2
                assert mock_process.call_count == 2


class TestRAGPipeline:
    """Test cases for RAGPipeline"""
    
    @pytest.fixture
    def rag_pipeline(self):
        mock_vector_store = AsyncMock()
        return RAGPipeline(mock_vector_store)
    
    @pytest.mark.asyncio
    async def test_generate_response(self, rag_pipeline):
        """Test generating RAG response"""
        mock_chunks = [
            {
                "content": "test content 1",
                "file_name": "test1.pdf"
            }
        ]
        
        rag_pipeline.vector_store.search_similar_chunks = AsyncMock(return_value=mock_chunks)
        
        with patch.object(rag_pipeline, '_query_llama', return_value="test response"):
            result = await rag_pipeline.generate_response("test query")
            
            assert result["response"] == "test response"
            assert result["sources"] == ["test1.pdf"]
    
    @pytest.mark.asyncio
    async def test_generate_response_no_chunks(self, rag_pipeline):
        """Test generating response when no chunks found"""
        rag_pipeline.vector_store.search_similar_chunks = AsyncMock(return_value=[])
        
        result = await rag_pipeline.generate_response("test query")
        
        assert "don't have any relevant information" in result["response"]
        assert result["sources"] == []
    
    def test_build_context(self, rag_pipeline):
        """Test building context from chunks"""
        chunks = [
            {
                "content": "content 1",
                "file_name": "file1.pdf"
            },
            {
                "content": "content 2",
                "file_name": "file2.pdf"
            }
        ]
        
        context = rag_pipeline._build_context(chunks)
        
        assert "Source 1 (from file1.pdf)" in context
        assert "content 1" in context
        assert "Source 2 (from file2.pdf)" in context
        assert "content 2" in context
    
    def test_create_rag_prompt(self, rag_pipeline):
        """Test creating RAG prompt"""
        query = "test question"
        context = "test context"
        
        prompt = rag_pipeline._create_rag_prompt(query, context)
        
        assert query in prompt
        assert context in prompt
        assert "Answer:" in prompt
    
    def test_create_rag_prompt_with_conversation(self, rag_pipeline):
        """Test creating RAG prompt with conversation context"""
        query = "test question"
        context = "test context"
        conversation_context = "User: hello\nAssistant: hi"
        
        prompt = rag_pipeline._create_rag_prompt(query, context, conversation_context)
        
        assert query in prompt
        assert context in prompt
        assert conversation_context in prompt
        assert "Conversation History:" in prompt


class TestConversationMemory:
    """Test cases for ConversationMemory"""
    
    @pytest.fixture
    def conversation_memory(self):
        return ConversationMemory()
    
    def test_add_message(self, conversation_memory):
        """Test adding message to conversation"""
        session_id = "test_session"
        conversation_memory.add_message(session_id, "user", "Hello")
        
        assert session_id in conversation_memory.conversations
        assert len(conversation_memory.conversations[session_id]) == 1
        assert conversation_memory.conversations[session_id][0]["role"] == "user"
        assert conversation_memory.conversations[session_id][0]["content"] == "Hello"
    
    def test_get_conversation_history(self, conversation_memory):
        """Test getting conversation history"""
        session_id = "test_session"
        conversation_memory.add_message(session_id, "user", "Hello")
        conversation_memory.add_message(session_id, "assistant", "Hi there")
        
        history = conversation_memory.get_conversation_history(session_id)
        
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[1]["role"] == "assistant"
    
    def test_get_conversation_context(self, conversation_memory):
        """Test getting formatted conversation context"""
        session_id = "test_session"
        conversation_memory.add_message(session_id, "user", "Hello")
        conversation_memory.add_message(session_id, "assistant", "Hi there")
        
        context = conversation_memory.get_conversation_context(session_id)
        
        assert "User: Hello" in context
        assert "Assistant: Hi there" in context
    
    def test_clear_conversation(self, conversation_memory):
        """Test clearing conversation"""
        session_id = "test_session"
        conversation_memory.add_message(session_id, "user", "Hello")
        
        assert session_id in conversation_memory.conversations
        
        conversation_memory.clear_conversation(session_id)
        
        assert session_id not in conversation_memory.conversations


class TestModels:
    """Test cases for Pydantic models"""
    
    def test_chat_request(self):
        """Test ChatRequest model"""
        request = ChatRequest(query="test query")
        assert request.query == "test query"
        assert request.session_id is None
        
        request_with_session = ChatRequest(query="test query", session_id="session123")
        assert request_with_session.session_id == "session123"
    
    def test_chat_response(self):
        """Test ChatResponse model"""
        response = ChatResponse(
            response="test response",
            sources=["source1.pdf", "source2.pdf"],
            session_id="session123"
        )
        
        assert response.response == "test response"
        assert response.sources == ["source1.pdf", "source2.pdf"]
        assert response.session_id == "session123"
    
    def test_pdf_metadata(self):
        """Test PDFMetadata model"""
        from datetime import datetime
        
        metadata = PDFMetadata(
            file_name="test.pdf",
            file_size=1024,
            processed_time=datetime.now(),
            chunk_count=5
        )
        
        assert metadata.file_name == "test.pdf"
        assert metadata.file_size == 1024
        assert metadata.chunk_count == 5
    
    def test_document_response(self):
        """Test DocumentResponse model"""
        from datetime import datetime
        
        pdf_metadata = PDFMetadata(
            file_name="test.pdf",
            file_size=1024,
            processed_time=datetime.now(),
            chunk_count=5
        )
        
        response = DocumentResponse(
            message="Success",
            processed_files=[pdf_metadata],
            total_chunks=5
        )
        
        assert response.message == "Success"
        assert len(response.processed_files) == 1
        assert response.total_chunks == 5


if __name__ == "__main__":
    pytest.main([__file__])
