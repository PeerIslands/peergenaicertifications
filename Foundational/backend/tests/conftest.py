"""Pytest configuration and fixtures."""
import os
import pytest
from httpx import AsyncClient
from unittest.mock import Mock, AsyncMock, patch
from typing import AsyncGenerator, Generator

# Set test environment variables before importing app
os.environ["OPENAI_API_KEY"] = "test-key-12345"
os.environ["MONGODB_URI"] = "mongodb://localhost:27017/test_chatpdf"
os.environ["DEBUG"] = "False"

from src.main import app


@pytest.fixture
def mock_openai():
    """Mock OpenAI API calls."""
    with patch('openai.resources.chat.completions.Completions.create') as mock:
        mock.return_value = Mock(
            choices=[Mock(message=Mock(content="Test response from AI"))]
        )
        yield mock


@pytest.fixture
def mock_embeddings():
    """Mock OpenAI embeddings."""
    with patch('openai.resources.embeddings.Embeddings.create') as mock:
        mock.return_value = Mock(
            data=[Mock(embedding=[0.1] * 1536)]
        )
        yield mock


@pytest.fixture
def mock_mongodb():
    """Mock MongoDB connection."""
    mock_db = Mock()
    mock_collection = Mock()
    
    # Setup collection methods
    mock_collection.insert_one = Mock(return_value=Mock(inserted_id="test_id_123"))
    mock_collection.find_one = Mock(return_value=None)
    mock_collection.find = Mock(return_value=[])
    mock_collection.delete_one = Mock(return_value=Mock(deleted_count=1))
    mock_collection.delete_many = Mock(return_value=Mock(deleted_count=1))
    
    mock_db.__getitem__ = Mock(return_value=mock_collection)
    
    with patch('pymongo.MongoClient') as mock_client:
        mock_client.return_value.__getitem__ = Mock(return_value=mock_db)
        yield mock_db


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Create async test client."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client


@pytest.fixture
def sample_pdf_file():
    """Create a sample PDF file content for testing."""
    # Minimal PDF file structure
    pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Test PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000214 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
307
%%EOF"""
    return pdf_content


@pytest.fixture
def mock_file_upload(sample_pdf_file):
    """Create mock file upload."""
    from io import BytesIO
    return BytesIO(sample_pdf_file)


@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Cleanup test files after each test."""
    yield
    # Add cleanup logic here if needed
    pass

