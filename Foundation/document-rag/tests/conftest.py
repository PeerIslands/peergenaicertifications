"""
Pytest configuration and fixtures for unit tests.
"""
import pytest
import sys
import os
from unittest.mock import Mock, MagicMock
from langchain_core.documents import Document

# Add parent directory to path to import app module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@pytest.fixture
def sample_documents():
    """Fixture providing sample documents for testing."""
    return [
        Document(
            page_content="This is a test document with some content.",
            metadata={"page": 0, "source_file": "test.pdf"}
        ),
        Document(
            page_content="This is another page of the document.",
            metadata={"page": 1, "source_file": "test.pdf"}
        )
    ]


@pytest.fixture
def mock_uploaded_file():
    """Fixture providing a mock uploaded file."""
    mock_file = Mock()
    mock_file.name = "test.pdf"
    mock_file.size = 1024
    mock_file.read.return_value = b"fake pdf content"
    return mock_file


@pytest.fixture
def mock_vector_store():
    """Fixture providing a mock vector store."""
    mock_store = Mock()
    mock_retriever = Mock()
    mock_store.as_retriever.return_value = mock_retriever
    return mock_store


@pytest.fixture
def mock_mongodb_uri():
    """Fixture providing a mock MongoDB connection string."""
    return "mongodb+srv://test:test@cluster.mongodb.net/"


@pytest.fixture
def mock_mongodb_config():
    """Fixture providing MongoDB configuration."""
    return {
        "uri": "mongodb+srv://test:test@cluster.mongodb.net/",
        "db_name": "test_db",
        "collection_name": "test_collection",
        "index_name": "vector_index"
    }

