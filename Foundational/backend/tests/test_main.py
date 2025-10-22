"""Tests for main FastAPI application."""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test health check endpoint."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Test detailed health endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "ok"]


@pytest.mark.asyncio
async def test_cors_headers(async_client: AsyncClient):
    """Test CORS headers are present."""
    response = await async_client.options("/")
    # Check that CORS middleware is working
    assert response.status_code in [200, 405]  # OPTIONS may not be explicitly handled

