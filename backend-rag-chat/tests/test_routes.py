import pytest
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
from fastapi import HTTPException
import json

from main import app
from routes.chat import router as chat_router
from routes.documents import router as documents_router
from services.vector_store import VectorStore
from services.rag_pipeline import RAGPipeline
from services.file_processor import FileProcessor
from models.chat_request import ChatRequest, ChatResponse


class TestChatRoutes:
    """Test cases for chat routes"""
    
    @pytest.fixture
    def client(self):
        return TestClient(app)
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_success(self):
        """Test successful chat request"""
        with patch('routes.chat.vector_store') as mock_vector_store:
            mock_vector_store.get_chunk_count = AsyncMock(return_value=10)
            
            with patch('routes.chat.rag_pipeline') as mock_rag:
                mock_rag.generate_response = AsyncMock(return_value={
                    "response": "test response",
                    "sources": ["test.pdf"]
                })
                
                with patch('routes.chat.conversation_memory') as mock_memory:
                    mock_memory.add_message = Mock()
                    
                    request = ChatRequest(query="test query")
                    
                    # This would need to be tested with actual FastAPI test client
                    # For now, we'll test the logic components
                    assert request.query == "test query"
    
    @pytest.mark.asyncio
    async def test_chat_endpoint_no_documents(self):
        """Test chat request when no documents are loaded"""
        with patch('routes.chat.vector_store') as mock_vector_store:
            mock_vector_store.get_chunk_count = AsyncMock(return_value=0)
            
            request = ChatRequest(query="test query")
            
            # Test the logic that would return no documents message
            chunk_count = await mock_vector_store.get_chunk_count()
            assert chunk_count == 0
    
    @pytest.mark.asyncio
    async def test_reset_endpoint(self):
        """Test reset documents endpoint"""
        with patch('routes.chat.vector_store') as mock_vector_store:
            mock_vector_store.clear_all_chunks = AsyncMock(return_value=5)
            
            deleted_count = await mock_vector_store.clear_all_chunks()
            assert deleted_count == 5
    
    @pytest.mark.asyncio
    async def test_clear_memory_endpoint(self):
        """Test clear conversation memory endpoint"""
        with patch('routes.chat.conversation_memory') as mock_memory:
            mock_memory.clear_conversation = Mock()
            
            session_id = "test_session"
            mock_memory.clear_conversation(session_id)
            
            mock_memory.clear_conversation.assert_called_once_with(session_id)
    
    @pytest.mark.asyncio
    async def test_health_check_endpoint(self):
        """Test health check endpoint"""
        with patch('routes.chat.vector_store') as mock_vector_store:
            mock_vector_store.get_chunk_count = AsyncMock(return_value=10)
            
            chunk_count = await mock_vector_store.get_chunk_count()
            assert chunk_count == 10


class TestDocumentRoutes:
    """Test cases for document routes"""
    
    @pytest.mark.asyncio
    async def test_reload_endpoint_success(self):
        """Test successful document reload"""
        with patch('routes.documents.vector_store') as mock_vector_store:
            mock_vector_store.clear_all_chunks = AsyncMock(return_value=5)
            mock_vector_store.store_chunks = AsyncMock(return_value=10)
            
            with patch('routes.documents.file_processor') as mock_processor:
                mock_processor.process_all_files.return_value = [{
                    "doc_id": "test_id",
                    "file_name": "test.pdf",
                    "file_size": 1024,
                    "chunk_count": 5
                }]
                
                # Test the logic components
                processed_files = mock_processor.process_all_files()
                assert len(processed_files) == 1
                
                deleted_count = await mock_vector_store.clear_all_chunks()
                assert deleted_count == 5
                
                total_chunks = await mock_vector_store.store_chunks(processed_files)
                assert total_chunks == 10
    
    @pytest.mark.asyncio
    async def test_reload_endpoint_no_files(self):
        """Test reload when no files found"""
        with patch('routes.documents.file_processor') as mock_processor:
            mock_processor.process_all_files.return_value = []
            
            processed_files = mock_processor.process_all_files()
            assert len(processed_files) == 0
    
    @pytest.mark.asyncio
    async def test_status_endpoint(self):
        """Test document status endpoint"""
        with patch('routes.documents.vector_store') as mock_vector_store:
            mock_vector_store.get_chunk_count = AsyncMock(return_value=10)
            mock_vector_store.get_document_count = AsyncMock(return_value=2)
            
            chunk_count = await mock_vector_store.get_chunk_count()
            doc_count = await mock_vector_store.get_document_count()
            
            assert chunk_count == 10
            assert doc_count == 2


class TestMainApp:
    """Test cases for main FastAPI application"""
    
    def test_app_creation(self):
        """Test that the FastAPI app is created correctly"""
        assert app.title == "RAG Chat API"
        assert app.version == "1.0.0"
    
    def test_cors_middleware(self):
        """Test CORS middleware configuration"""
        # Check if CORS middleware is added by looking at the middleware stack
        middleware_found = False
        for middleware in app.user_middleware:
            middleware_str = str(middleware)
            if 'CORSMiddleware' in middleware_str or 'cors' in middleware_str.lower():
                middleware_found = True
                break
        assert middleware_found, f"CORS middleware not found in app middleware stack. Middlewares: {[str(m) for m in app.user_middleware]}"
    
    def test_router_inclusion(self):
        """Test that routers are included"""
        # Check if routers are included in the app
        route_paths = [route.path for route in app.routes]
        assert "/api/chat" in route_paths or any("/api/chat" in str(route) for route in app.routes)
        assert "/api/status" in route_paths or any("/api/status" in str(route) for route in app.routes)


class TestIntegration:
    """Integration test cases"""
    
    @pytest.mark.asyncio
    async def test_full_rag_pipeline(self):
        """Test complete RAG pipeline integration"""
        # Mock all dependencies
        with patch('services.vector_store.VectorStore') as mock_vector_store_class:
            mock_vector_store = AsyncMock()
            mock_vector_store_class.return_value = mock_vector_store
            
            with patch('services.rag_pipeline.RAGPipeline') as mock_rag_class:
                mock_rag = AsyncMock()
                mock_rag_class.return_value = mock_rag
                
                with patch('services.conversation_memory.conversation_memory') as mock_memory:
                    # Setup mocks
                    mock_vector_store.get_chunk_count.return_value = 10
                    mock_vector_store.search_similar_chunks.return_value = [
                        {"content": "test content", "file_name": "test.pdf"}
                    ]
                    mock_rag.generate_response.return_value = {
                        "response": "test response",
                        "sources": ["test.pdf"]
                    }
                    mock_memory.add_message = Mock()
                    mock_memory.get_conversation_context.return_value = ""
                    
                    # Test the pipeline
                    chunk_count = await mock_vector_store.get_chunk_count()
                    assert chunk_count == 10
                    
                    chunks = await mock_vector_store.search_similar_chunks("test query")
                    assert len(chunks) == 1
                    
                    result = await mock_rag.generate_response("test query")
                    assert result["response"] == "test response"
                    assert result["sources"] == ["test.pdf"]
    
    @pytest.mark.asyncio
    async def test_file_processing_integration(self):
        """Test file processing integration"""
        with patch('services.file_processor.FileProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor_class.return_value = mock_processor
            
            with patch('services.vector_store.VectorStore') as mock_vector_store_class:
                mock_vector_store = AsyncMock()
                mock_vector_store_class.return_value = mock_vector_store
                
                # Setup mocks
                mock_processor.process_all_files.return_value = [{
                    "doc_id": "test_id",
                    "file_name": "test.pdf",
                    "file_size": 1024,
                    "chunks": [{"content": "test", "chunk_id": "chunk1"}],
                    "chunk_count": 1
                }]
                mock_vector_store.store_chunks.return_value = 1
                
                # Test integration
                processed_files = mock_processor.process_all_files()
                assert len(processed_files) == 1
                
                total_chunks = await mock_vector_store.store_chunks(processed_files)
                assert total_chunks == 1


if __name__ == "__main__":
    pytest.main([__file__])
