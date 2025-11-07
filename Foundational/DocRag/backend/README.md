# RAG PDF Query Backend

FastAPI backend for PDF document ingestion and RAG-based querying using LangChain, FAISS, HuggingFace embeddings, and Azure OpenAI.

## Features

- 🚀 **Local Embeddings**: Uses HuggingFace embeddings (free, no API costs)
- 💬 **Azure OpenAI**: GPT-4o for answer generation
- 📄 **PDF Processing**: Automatic document chunking and ingestion
- 🔍 **Vector Search**: FAISS for fast similarity search
- 🌐 **REST API**: FastAPI with CORS support

## Setup

1. **Create a virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

Note: On first run, the HuggingFace embedding model (~80MB) will be downloaded automatically and cached locally.

3. **Configure environment variables:**
Create a `.env` file in the backend directory with your Azure OpenAI credentials:

```env
# Azure OpenAI Configuration
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4o
AZURE_OPENAI_API_VERSION=2024-10-21
```

**Required variables:**
- `AZURE_OPENAI_API_KEY`: Your Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_CHAT_DEPLOYMENT`: Your chat model deployment name (e.g., gpt-4o, gpt-4, gpt-35-turbo)
- `AZURE_OPENAI_API_VERSION`: API version (2024-10-21 recommended)

**Note**: No embedding deployment needed! We use free HuggingFace embeddings locally.

4. **Run the server:**
```bash
python main.py
```

Or with uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /
Health check endpoint

### POST /api/ingest
Upload and ingest PDF files
- Request: multipart/form-data with PDF files
- Response: Success message with file count

### POST /api/query
Query the ingested documents
- Request: `{"query": "your question", "top_k": 3}`
- Response: `{"answer": "...", "sources": [...]}`

### GET /api/status
Get system status
- Response: `{"initialized": true/false, "documents_count": number}`

### DELETE /api/reset
Reset the RAG system and clear all documents

## PDF Directory

Place your PDF files in the `pdfs/` directory. You can either:
1. Add PDFs manually to this folder
2. Upload PDFs via the `/api/ingest` endpoint

## Architecture

### Core Components

- **FastAPI**: REST API framework with CORS support (ports 3000, 3001, 5173)
- **LangChain 0.3.x**: RAG orchestration and document processing
  - `langchain-community`: Document loaders and vector stores
  - `langchain-text-splitters`: Text chunking utilities
  - `langchain-huggingface`: HuggingFace embeddings integration
- **FAISS (CPU)**: Vector store for fast similarity search
- **HuggingFace Embeddings**: Free, local embeddings using `sentence-transformers/all-MiniLM-L6-v2`
- **Azure OpenAI**: Direct client integration for chat completions (GPT-4o)
- **PyPDF**: PDF document parsing

### Data Flow

1. **Document Ingestion**: PDFs → PyPDF → Text Chunks → HuggingFace Embeddings → FAISS Vector Store
2. **Query Processing**: User Query → Retrieve Relevant Chunks (FAISS) → Azure OpenAI (GPT-4o) → Answer + Sources

### Dependencies

Key packages:
- `fastapi>=0.104.1`
- `langchain>=0.3.0`
- `langchain-community>=0.3.0`
- `langchain-openai>=0.2.0`
- `langchain-text-splitters>=0.3.0`
- `langchain-huggingface>=0.1.0`
- `sentence-transformers>=2.2.0`
- `openai>=1.51.0`
- `faiss-cpu>=1.7.4`

