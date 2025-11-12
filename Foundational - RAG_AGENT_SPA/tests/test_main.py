import pytest
from fastapi.testclient import TestClient


def test_root_endpoint(client):
    """Test main page loads correctly"""
    response = client.get("/")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "RAG Document QA System" in response.text


def test_health_check(client):
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
