from __future__ import annotations

import io
import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_index_served():
    r = client.get("/")
    assert r.status_code == 200
    assert "ChatWithDoc" in r.text


def test_list_pdfs_empty(monkeypatch):
    # Mock list_sources to avoid touching real DB
    from app import rag_service

    monkeypatch.setattr(rag_service, "list_sources", lambda: [])
    r = client.get("/api/pdfs")
    assert r.status_code == 200
    assert r.json() == {"sources": []}


def test_upload_pdf_validation():
    # Non-PDF should fail
    files = {"files": ("bad.txt", b"hello", "text/plain")}
    r = client.post("/api/upload", files=files)
    assert r.status_code == 400


def test_query_validation():
    r = client.post("/api/query", json={"question": "", "strategy": "similarity", "k": 4})
    assert r.status_code in (400, 422)


