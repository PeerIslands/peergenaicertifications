import os
from dataclasses import dataclass


def _project_root() -> str:
    # src/config/settings.py -> src/config -> src -> <root>
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@dataclass(frozen=True)
class Settings:
    # Ollama
    ollama_llm_model: str = os.getenv("OLLAMA_LLM_MODEL", "llama3.1")
    ollama_embed_model: str = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

    # Paths
    project_root: str = _project_root()
    data_dir: str = os.path.join(_project_root(), "data")
    pdf_dir: str = os.path.join(_project_root(), "data", "pdfs")
    queries_file: str = os.path.join(_project_root(), "data", "queries", "Queries.md")
    reports_dir: str = os.path.join(_project_root(), "reports")


def ensure_directories_exist(settings: Settings) -> None:
    os.makedirs(settings.data_dir, exist_ok=True)
    os.makedirs(settings.pdf_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.project_root, "data", "queries"), exist_ok=True)
    os.makedirs(settings.reports_dir, exist_ok=True)


