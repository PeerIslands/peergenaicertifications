import os
import types
import pytest
from fastapi.testclient import TestClient

from src.api.main import create_app


@pytest.fixture(autouse=True)
def mock_rag(monkeypatch):
    class DummyQA:
        def invoke(self, query: str):
            return {"result": f"echo: {query}", "source_documents": []}

    # Patch the symbol used by the API module
    import src.api.main as api_main
    monkeypatch.setattr(api_main, "initialize_rag_system", lambda *args, **kwargs: DummyQA())


def test_health_ok():
    app = create_app()
    client = TestClient(app)
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] in {"ok", "degraded"}


def test_query_validation():
    app = create_app()
    client = TestClient(app)
    res = client.post("/query", json={"query": ""})
    assert res.status_code == 400


def test_query_success():
    app = create_app()
    client = TestClient(app)
    res = client.post("/query", json={"query": "hello"})
    assert res.status_code == 200
    body = res.json()
    assert body["result"].startswith("echo: ")

