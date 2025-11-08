import pytest
import os
from unittest.mock import MagicMock


@pytest.fixture(scope="session", autouse=True)
def mock_env_vars():
    os.environ["OPENAI_API_KEY"] = "test-api-key"
    os.environ["MONGODB_URI"] = "mongodb://localhost:27017/"
    os.environ["MONGODB_DB_NAME"] = "test_rag_database"
    os.environ["MONGODB_COLLECTION_NAME"] = "test_documents"
    os.environ["LOG_LEVEL"] = "ERROR"
    yield


@pytest.fixture
def mock_mongodb_client(mocker):
    mock_client = MagicMock()
    mock_db = MagicMock()
    mock_collection = MagicMock()

    mock_client.__getitem__.return_value = mock_db
    mock_db.__getitem__.return_value = mock_collection
    mock_client.admin.command = MagicMock(return_value={"ok": 1})

    mocker.patch("pymongo.MongoClient", return_value=mock_client)
    mocker.patch("mongodb_client.MongoClient", return_value=mock_client)
    return mock_collection


@pytest.fixture
def mock_sentence_transformer(mocker):
    mock_model = MagicMock()
    mock_model.encode.return_value = [[0.1] * 384 for _ in range(5)]
    mocker.patch("sentence_transformers.SentenceTransformer", return_value=mock_model)
    return mock_model


@pytest.fixture
def mock_openai_client(mocker):
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_choice = MagicMock()
    mock_message = MagicMock()

    mock_message.content = "Test response"
    mock_choice.message = mock_message
    mock_response.choices = [mock_choice]

    mock_client.chat.completions.create.return_value = mock_response

    mocker.patch("openai.OpenAI", return_value=mock_client)
    return mock_client


@pytest.fixture
def sample_document_data():
    return {
        "filename": "test.pdf",
        "text": "This is a test document.",
        "chunks": ["This is a test document."],
        "embeddings": [[0.1] * 384],
        "num_chunks": 1,
    }


@pytest.fixture
def sample_uploaded_file():
    mock_file = MagicMock()
    mock_file.name = "test.txt"
    mock_file.read.return_value = b"This is test content."
    return mock_file
