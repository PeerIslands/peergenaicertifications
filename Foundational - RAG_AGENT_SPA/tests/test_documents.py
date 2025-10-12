import pytest
from fastapi.testclient import TestClient


def test_document_count(client):
    """Test getting document count"""
    response = client.get("/documents/count")
    assert response.status_code == 200
    assert "document_count" in response.json()


def test_document_list(client):
    """Test getting document list"""
    response = client.get("/documents/list")
    assert response.status_code == 200
    assert "documents" in response.json()


def test_clear_documents(client):
    """Test clearing all documents"""
    response = client.delete("/documents")
    assert response.status_code == 200
    assert "cleared successfully" in response.json()["message"]
