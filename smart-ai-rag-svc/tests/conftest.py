"""
Pytest configuration and shared fixtures.
"""
import pytest
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
import tempfile
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up test environment variables."""
    monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key-1234567890abcdefghijklmnop")
    monkeypatch.setenv("MONGODB_URI", "mongodb://localhost:27017")
    monkeypatch.setenv("MONGODB_DATABASE", "test_rag_database")
    monkeypatch.setenv("MONGODB_COLLECTION", "test_documents")
    monkeypatch.setenv("VECTOR_INDEX_NAME", "test_vector_index")
    monkeypatch.setenv("CHUNK_SIZE", "1000")
    monkeypatch.setenv("CHUNK_OVERLAP", "200")
    monkeypatch.setenv("ENVIRONMENT", "test")


@pytest.fixture
def mock_settings(mock_env_vars):
    """Mock settings object."""
    with patch('src.config.settings.settings') as mock:
        mock.openai_api_key = "sk-test-key"
        mock.mongodb_uri = "mongodb://localhost:27017"
        mock.mongodb_database = "test_db"
        mock.mongodb_collection = "test_collection"
        mock.vector_index_name = "test_index"
        mock.embedding_model = "text-embedding-ada-002"
        mock.llm_model = "gpt-3.5-turbo"
        mock.chunk_size = 1000
        mock.chunk_overlap = 200
        mock.temperature = 0.7
        mock.max_tokens = 1000
        mock.top_k_results = 5
        mock.similarity_threshold = 0.7
        mock.sentence_window_size = 3
        yield mock


@pytest.fixture
def mock_mongodb_client():
    """Mock MongoDB client."""
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()
    
    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    mock_db.command.return_value = {"size": 1000, "avgObjSize": 100}
    
    mock_collection.count_documents.return_value = 10
    mock_collection.insert_many.return_value = MagicMock(
        inserted_ids=["id1", "id2", "id3"]
    )
    mock_collection.find_one.return_value = {
        "_id": "test-id",
        "text": "Test document",
        "metadata": {"source": "test.pdf"}
    }
    mock_collection.find.return_value = [
        {"text": "Doc 1", "metadata": {"source": "test1.pdf"}},
        {"text": "Doc 2", "metadata": {"source": "test2.pdf"}}
    ]
    mock_collection.delete_one.return_value = MagicMock(deleted_count=1)
    mock_collection.delete_many.return_value = MagicMock(deleted_count=2)
    mock_collection.update_one.return_value = MagicMock(modified_count=1)
    mock_collection.list_indexes.return_value = [
        {"name": "test_index", "key": {"embedding": 1}}
    ]
    
    return mock_client


@pytest.fixture
def sample_document():
    """Sample LangChain document."""
    from langchain_core.documents import Document
    return Document(
        page_content="This is a test document content.",
        metadata={"source": "test.pdf", "page": 1}
    )


@pytest.fixture
def sample_documents():
    """List of sample documents."""
    from langchain_core.documents import Document
    return [
        Document(
            page_content="Document 1 content",
            metadata={"source": "doc1.pdf", "page": 1}
        ),
        Document(
            page_content="Document 2 content",
            metadata={"source": "doc2.pdf", "page": 1}
        )
    ]


@pytest.fixture
def sample_question():
    """Sample question."""
    return "What is the main topic of this document?"


@pytest.fixture
def temp_pdf_file():
    """Create a temporary PDF file."""
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as f:
        # Minimal valid PDF
        f.write(b'%PDF-1.4\n')
        f.write(b'1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n')
        f.write(b'2 0 obj<</Type/Pages/Count 1/Kids[3 0 R]>>endobj\n')
        f.write(b'3 0 obj<</Type/Page/Parent 2 0 R>>endobj\n')
        f.write(b'xref\n0 4\ntrailer<</Size 4/Root 1 0 R>>\nstartxref\n')
        temp_path = f.name
    
    yield temp_path
    
    Path(temp_path).unlink(missing_ok=True)


@pytest.fixture
def mock_rag_service():
    """Mock RAG service."""
    mock = MagicMock()
    mock.load_and_index_documents.return_value = {
        "success": True,
        "message": "Documents indexed successfully",
        "document_stats": {"total_documents": 1, "total_nodes": 5},
        "processing_time": 0.5
    }
    mock.ask_question.return_value = {
        "success": True,
        "answer": "This is a test answer.",
        "sources": [
            {
                "chunk_id": 0,
                "content_preview": "Test content preview",
                "metadata": {"source": "test.pdf"}
            }
        ],
        "num_sources": 1,
        "processing_time": 0.5,
        "timestamp": datetime.now().isoformat(),
        "query_engine": "llamaindex"
    }
    mock.get_conversation_history.return_value = []
    mock.get_service_stats.return_value = {
        "llm_model": "gpt-3.5-turbo",
        "embedding_model": "text-embedding-ada-002",
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "top_k_results": 5,
        "similarity_threshold": 0.7,
        "conversation_history_length": 0,
        "vector_store_stats": {"document_count": 10}
    }
    return mock


@pytest.fixture
def mock_rag_evaluator():
    """Mock RAG evaluator."""
    mock = MagicMock()
    mock.evaluate_rag_response.return_value = {
        "question": "Test question",
        "answer": "Test answer",
        "metrics": {
            "answer_relevance": 0.85,
            "context_relevance": 0.80,
            "groundedness": 0.90,
            "overall_quality": 0.85
        },
        "context_stats": {
            "total_contexts": 3,
            "avg_context_length": 200
        },
        "evaluation_time": 0.5,
        "timestamp": datetime.now().isoformat()
    }
    mock.get_evaluation_summary.return_value = "Excellent quality response"
    return mock


@pytest.fixture
def mock_openai_embeddings():
    """Mock OpenAI embeddings."""
    with patch('langchain_openai.OpenAIEmbeddings') as mock:
        instance = MagicMock()
        instance.embed_query.return_value = [0.1] * 1536
        instance.embed_documents.return_value = [[0.1] * 1536]
        mock.return_value = instance
        yield mock


@pytest.fixture
def mock_openai_llm():
    """Mock OpenAI LLM."""
    with patch('langchain_openai.ChatOpenAI') as mock:
        instance = MagicMock()
        instance.invoke.return_value = MagicMock(content="Test response")
        mock.return_value = instance
        yield mock
