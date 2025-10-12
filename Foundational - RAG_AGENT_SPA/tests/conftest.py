import pytest
import os
import sys
from pathlib import Path

# Add the parent directory to Python path so we can import main
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
sys.path.insert(0, str(parent_dir))

try:
    from main import app
    from fastapi.testclient import TestClient
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Parent directory: {parent_dir}")
    print(f"Python path: {sys.path}")
    raise


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def sample_document():
    """Create sample document for testing"""
    return {
        "filename": "test_sample_document.txt",
        "content": "This is a test document about artificial intelligence."
    }


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment"""
    # Set a valid test API key (use a real one for testing)
    original_key = os.environ.get("GEMINI_API_KEY")
    os.environ["GEMINI_API_KEY"] = "test_api_key_placeholder"
    yield
    # Restore original key
    if original_key:
        os.environ["GEMINI_API_KEY"] = original_key
    else:
        os.environ.pop("GEMINI_API_KEY", None)
