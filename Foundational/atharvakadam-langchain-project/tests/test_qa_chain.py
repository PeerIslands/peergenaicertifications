# pyright: reportMissingImports=false

# tests/test_qa_chain.py
import pytest

from src.services import qa_chain
from src.services.qa_chain import _format_docs, handle_user_query, create_qa_chain


class DummyDoc:
    def __init__(self, content: str):
        self.page_content = content


def test_format_docs_joins_page_content_with_separator():
    docs = [DummyDoc("Page 1"), DummyDoc("Page 2")]
    result = _format_docs(docs)
    assert result == "Page 1\n\nPage 2"


def test_handle_user_query_invokes_chain():
    class DummyChain:
        def __init__(self):
            self.last_input = None

        def invoke(self, data):
            self.last_input = data
            return f"answer to: {data['question']}"

    chain = DummyChain()
    result = handle_user_query(chain, "What is RAG?")

    assert result == "answer to: What is RAG?"
    assert chain.last_input == {"question": "What is RAG?"}


def test_create_qa_chain_uses_tempfile_and_calls_build_chain(monkeypatch, tmp_path):
    """
    We mock PyPDFLoader and _build_chain so the test doesn't need a real PDF or FAISS/Ollama.
    """

    # Mock PyPDFLoader to ignore the actual file and return dummy pages
    class DummyLoader:
        def __init__(self, path):
            self.path = path

        def load_and_split(self):
            return [DummyDoc("dummy page content")]

    monkeypatch.setattr(qa_chain, "PyPDFLoader", DummyLoader)

    # Capture calls to _build_chain
    called = {"flag": False, "pages": None}

    def fake_build_chain(pages):
        called["flag"] = True
        called["pages"] = pages
        return "dummy_chain_object"

    monkeypatch.setattr(qa_chain, "_build_chain", fake_build_chain)

    # Fake uploaded file object with .read()
    class FakeUpload:
        def read(self):
            return b"%PDF-1.4 fake pdf bytes"

    chain = create_qa_chain(FakeUpload())

    assert chain == "dummy_chain_object"
    assert called["flag"] is True
    assert isinstance(called["pages"], list)
    assert len(called["pages"]) == 1
    assert isinstance(called["pages"][0], DummyDoc)
