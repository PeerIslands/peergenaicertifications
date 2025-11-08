import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from mongodb_client import MongoDBClient
from pymongo.errors import ConnectionFailure, OperationFailure


class TestMongoDBClient:

    def test_mongodb_client_initialization(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        assert client is not None
        assert client.collection is not None

    def test_mongodb_client_initialization_without_uri(self, mocker):
        with patch("mongodb_client.MONGODB_URI", ""):
            with pytest.raises(ValueError, match="MongoDB URI is not configured"):
                MongoDBClient()

    def test_validate_document_data_success(
        self, mock_env_vars, mock_mongodb_client, sample_document_data
    ):
        client = MongoDBClient()
        assert client._validate_document_data(sample_document_data) is True

    def test_validate_document_data_missing_field(
        self, mock_env_vars, mock_mongodb_client
    ):
        client = MongoDBClient()
        invalid_data = {"filename": "test.pdf"}
        with pytest.raises(ValueError, match="Missing required field"):
            client._validate_document_data(invalid_data)

    def test_validate_document_data_empty_filename(
        self, mock_env_vars, mock_mongodb_client
    ):
        client = MongoDBClient()
        invalid_data = {
            "filename": "",
            "text": "test",
            "chunks": ["test"],
            "embeddings": [[0.1]],
            "num_chunks": 1,
        }
        with pytest.raises(ValueError, match="Filename must be a non-empty string"):
            client._validate_document_data(invalid_data)

    def test_validate_document_data_mismatched_chunks_embeddings(
        self, mock_env_vars, mock_mongodb_client
    ):
        client = MongoDBClient()
        invalid_data = {
            "filename": "test.pdf",
            "text": "test",
            "chunks": ["test1", "test2"],
            "embeddings": [[0.1]],
            "num_chunks": 2,
        }
        with pytest.raises(
            ValueError, match="Number of chunks must match number of embeddings"
        ):
            client._validate_document_data(invalid_data)

    def test_store_document_success(
        self, mock_env_vars, mock_mongodb_client, sample_document_data
    ):
        client = MongoDBClient()
        mock_result = MagicMock()
        mock_result.inserted_id = "test_id_123"
        client.collection.insert_one.return_value = mock_result

        result = client.store_document(sample_document_data)
        assert result == "test_id_123"
        client.collection.insert_one.assert_called_once()

    def test_store_document_with_invalid_data(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        invalid_data = {"filename": "test.pdf"}
        with pytest.raises(ValueError):
            client.store_document(invalid_data)

    def test_get_all_documents(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        mock_cursor = [
            {
                "_id": "123",
                "filename": "test.pdf",
                "timestamp": "2024-01-01",
                "num_chunks": 5,
            }
        ]
        client.collection.find.return_value = mock_cursor

        documents = client.get_all_documents()
        assert len(documents) == 1
        assert documents[0]["filename"] == "test.pdf"

    def test_cosine_similarity_calculation(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        vec1 = [1.0, 0.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        similarity = client.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(1.0, 0.001)

    def test_cosine_similarity_orthogonal_vectors(
        self, mock_env_vars, mock_mongodb_client
    ):
        client = MongoDBClient()
        vec1 = [1.0, 0.0]
        vec2 = [0.0, 1.0]
        similarity = client.cosine_similarity(vec1, vec2)
        assert similarity == pytest.approx(0.0, 0.001)

    def test_cosine_similarity_empty_vectors(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        with pytest.raises(ValueError, match="Vectors cannot be empty"):
            client.cosine_similarity([], [1.0])

    def test_cosine_similarity_mismatched_dimensions(
        self, mock_env_vars, mock_mongodb_client
    ):
        client = MongoDBClient()
        vec1 = [1.0, 0.0]
        vec2 = [1.0, 0.0, 0.0]
        with pytest.raises(ValueError, match="Vector dimensions must match"):
            client.cosine_similarity(vec1, vec2)

    def test_cosine_similarity_zero_vector(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        vec1 = [0.0, 0.0]
        vec2 = [1.0, 0.0]
        similarity = client.cosine_similarity(vec1, vec2)
        assert similarity == 0

    def test_similarity_search_success(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        mock_docs = [
            {
                "_id": "123",
                "filename": "test.pdf",
                "chunks": [
                    {
                        "chunk_id": 0,
                        "text": "test content",
                        "embedding": [1.0, 0.0, 0.0],
                    }
                ],
            }
        ]
        client.collection.find.return_value = mock_docs

        query_embedding = [1.0, 0.0, 0.0]
        results = client.similarity_search(query_embedding, top_k=5)
        assert len(results) <= 5

    def test_similarity_search_empty_query(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        with pytest.raises(ValueError, match="Query embedding cannot be empty"):
            client.similarity_search([], top_k=5)

    def test_similarity_search_invalid_top_k(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        with pytest.raises(ValueError, match="top_k must be a positive integer"):
            client.similarity_search([1.0, 0.0], top_k=0)

    def test_delete_document_success(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        mock_result = MagicMock()
        mock_result.deleted_count = 1
        client.collection.delete_one.return_value = mock_result

        result = client.delete_document("507f1f77bcf86cd799439011")
        assert result is True

    def test_delete_document_invalid_id(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        with pytest.raises(ValueError, match="Invalid document ID format"):
            client.delete_document("invalid_id")

    def test_delete_document_empty_id(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        with pytest.raises(ValueError, match="Document ID must be a non-empty string"):
            client.delete_document("")

    def test_clear_all_documents(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        mock_result = MagicMock()
        mock_result.deleted_count = 5
        client.collection.delete_many.return_value = mock_result

        deleted_count = client.clear_all_documents()
        assert deleted_count == 5

    def test_close_connection(self, mock_env_vars, mock_mongodb_client):
        client = MongoDBClient()
        client.close_connection()

    def test_close_all_connections(self, mock_env_vars, mock_mongodb_client):
        MongoDBClient.close_all_connections()
