## ChatWithDoc - Single Page RAG App (FastAPI + LangChain + Chroma)

This project is a single-page Retrieval Augmented Generation (RAG) application built with FastAPI (backend), LangChain (chunking, retrieval), OpenAI embeddings (default) with Gemini fallback, and Chroma as the vector database. It supports CRUD operations for PDFs, querying with multiple retrieval strategies (similarity, MMR, rerank, map_reduce), and clear error handling.

### Features
- Upload, list, and delete PDFs
- Automatic PDF parsing, chunking, embedding using OpenAI (`text-embedding-3-small`) by default, falls back to Gemini (`models/gemini-embedding-001`) if OpenAI key is missing
- Vector storage in Chroma (persistent)
- Query with strategies: similarity, mmr (max marginal relevance), rerank, and map_reduce
- Frontend single-page app (vanilla JS) served by FastAPI
- Robust validation and error handling
- Pytest test suite

### Prerequisites
- Python 3.10+
- One of: OpenAI API key (preferred) or a Google Generative AI (Gemini) API key

### Quick Start

1) Create virtual environment and install dependencies

```bash
bash scripts/setup.sh
```

2) Provide your environment configuration

Create `.env` with either OpenAI or Gemini settings. If both are present, OpenAI is used.

```env
# OpenAI (preferred)
OPENAI_API_KEY=replace-with-your-key
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_CHAT_MODEL=gpt-4o-mini

# Infra
CHROMA_DIR=./chroma_db
UPLOAD_DIR=./uploads
```

3) Run the server

```bash
source .venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

Open the app at `http://localhost:8000`.

### Environment Variables
- `OPENAI_API_KEY` (preferred): Enables OpenAI embeddings/LLM
- `GOOGLE_API_KEY` (fallback): Enables Gemini embeddings/LLM; see Gemini embeddings docs: [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)
- `CHROMA_DIR`: Directory for Chroma persistence (default: `./chroma_db`)
- `UPLOAD_DIR`: Directory for uploaded PDFs (default: `./uploads`)
- `OPENAI_EMBEDDING_MODEL`: Default `text-embedding-3-small`
- `OPENAI_CHAT_MODEL`: Default `gpt-4o-mini`
- `GEMINI_EMBEDDING_MODEL`: Must be `models/gemini-embedding-001`
- `GEMINI_CHAT_MODEL`: Default `gemini-1.5-flash`

### Available Retrieval Strategies
- `similarity`: top-k similarity search
- `mmr`: diverse results using max marginal relevance
- `rerank`: fetch candidates and rerank by score
- `map_reduce`: synthesizes response using an LLM over retrieved chunks (uses OpenAI if available; otherwise Gemini)

### Run Tests

```bash
source .venv/bin/activate
pytest -q
```

### Notes
- Provider priority: OpenAI -> Gemini. If neither key is available, the server will reject queries that require embeddings.
- Gemini embeddings reference: [Gemini embeddings](https://ai.google.dev/gemini-api/docs/embeddings)


