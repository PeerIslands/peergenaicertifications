# Smart AI RAG Service

**Submitted by:** Suresh Selvam  
**Branch:** `sureshselvam`  
**Project Location:** `smart-ai-rag-svc/`

---

## What This Service Does

A **Retrieval-Augmented Generation (RAG) service** that enables intelligent question-answering over PDF documents. Upload your documents, ask questions, and get accurate AI-powered answers based on the content.

### Core Capabilities

1. **Document Processing**
   - Upload PDF files via REST API
   - Automatically extracts and chunks text
   - Creates semantic embeddings
   - Stores in MongoDB Vector Search

2. **Intelligent Q&A**
   - Ask natural language questions
   - Retrieves relevant document chunks using vector similarity
   - Generates accurate answers using OpenAI GPT models
   - Provides source citations with each answer

3. **Quality Evaluation**
   - Measures answer relevance to the question
   - Assesses context relevance of retrieved chunks
   - Detects hallucinations (groundedness check)
   - Provides quality scores and recommendations

4. **Dual Framework Support**
   - **LangChain**: Character-based chunking
   - **LlamaIndex**: Sentence-based parsing
   - Switch between frameworks via API parameter

---

## Technology Stack

- **Language**: Python 3.8+
- **API Framework**: FastAPI
- **RAG Frameworks**: LangChain, LlamaIndex
- **LLM**: OpenAI GPT-3.5/GPT-4
- **Embeddings**: OpenAI text-embedding-ada-002
- **Vector Database**: MongoDB Atlas Vector Search
- **Evaluation**: TruLens

---

## How to Run

```bash
# 1. Setup
cd smart-ai-rag-svc
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
# Edit .env with your OPENAI_API_KEY and MONGODB_URI

# 3. Setup database
python scripts/setup_mongodb_index.py

# 4. Start service
python main.py
```

Service runs at: `http://localhost:8000`

---

## API Usage

### 1. Upload a Document
```bash
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=true" \
  -F "file=@document.pdf"
```

### 2. Ask a Question
```bash
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?", "k": 5}'
```

**Response:**
```json
{
  "answer": "The document is about...",
  "sources": [...],
  "num_sources": 3,
  "processing_time": 1.2
}
```

### 3. Evaluate Answer Quality
```bash
curl -X POST "http://localhost:8000/evaluate/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key points?", "use_llamaindex": true}'
```

**Response:**
```json
{
  "rag_response": {
    "answer": "...",
    "sources": [...]
  },
  "evaluation": {
    "metrics": {
      "answer_relevance": 0.95,
      "context_relevance": 0.88,
      "groundedness": 0.92,
      "overall_quality": 0.91
    }
  }
}
```

---

## API Endpoints

| Endpoint | Method | What It Does |
|----------|--------|--------------|
| `/health` | GET | Check if service is running |
| `/documents/upload-file` | POST | Upload and index a PDF |
| `/questions/ask` | POST | Ask a question about uploaded documents |
| `/evaluate/query` | POST | Ask question and get quality evaluation |
| `/conversation/history` | GET | Retrieve conversation history |
| `/conversation/history` | DELETE | Clear conversation history |
| `/stats` | GET | Get service statistics |

---

## Project Structure

```
smart-ai-rag-svc/
├── main.py                        # FastAPI application entry point
├── requirements.txt               # Python dependencies
├── .env.example                   # Configuration template
│
├── src/
│   ├── config/settings.py        # Environment configuration
│   ├── models/schemas.py         # API request/response models
│   ├── services/
│   │   └── enhanced_rag_service.py   # Main RAG implementation
│   └── utils/
│       ├── document_processor.py     # LangChain document processing
│       ├── llamaindex_processor.py   # LlamaIndex document processing
│       └── rag_evaluator.py          # TruLens quality evaluation
│
├── scripts/
│   └── setup_mongodb_index.py    # Database setup
│
└── examples/
    ├── quickstart.py              # Quick start guide
    └── example_usage.py           # Detailed examples
```

---

## Configuration

Required environment variables (see `.env.example`):

```env
# OpenAI
OPENAI_API_KEY=sk-your-key-here
OPENAI_LLM_MODEL=gpt-3.5-turbo
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002

# MongoDB Atlas
MONGODB_URI=mongodb+srv://...
MONGODB_DATABASE=rag_database
MONGODB_COLLECTION=documents

# RAG Settings
TOP_K_RESULTS=5                    # Number of chunks to retrieve
SIMILARITY_THRESHOLD=0.7           # Minimum relevance score
CHUNK_SIZE=500                     # Text chunk size (LangChain)
SENTENCE_WINDOW_SIZE=3             # Context window (LlamaIndex)
```

---

## What Makes This Service Production-Ready

- ✅ **Error Handling**: Clear error messages for all failure cases
- ✅ **Dual Frameworks**: Compare LangChain vs LlamaIndex performance
- ✅ **Quality Metrics**: Automated evaluation with TruLens
- ✅ **Vector Search**: Efficient similarity search with MongoDB Atlas
- ✅ **REST API**: Standard HTTP endpoints with OpenAPI docs
- ✅ **Professional Responses**: Direct, concise answers
- ✅ **Conversation Context**: Maintains history for follow-up questions

---

## Dependencies

Core libraries (see `requirements.txt` for complete list):
- `fastapi` - REST API framework
- `langchain` - RAG framework #1
- `llama-index` - RAG framework #2
- `openai` - LLM and embeddings
- `pymongo` - MongoDB integration
- `trulens` - Quality evaluation

---

## Documentation

- **README.md**: Complete setup and usage guide
- **examples/**: Python code examples
- **API Docs**: Auto-generated at `http://localhost:8000/docs`

---

## Submission Summary

**What this project demonstrates:**
- Building production RAG systems
- Integrating multiple AI frameworks (LangChain + LlamaIndex)
- Vector database implementation (MongoDB Atlas)
- API development with FastAPI
- AI quality evaluation (TruLens)
- Clean, modular Python architecture

**Total Deliverable:**
- 25+ source files
- 5,000+ lines of code
- Comprehensive documentation
- Working examples
- Production-ready error handling

---

**For detailed documentation, see `smart-ai-rag-svc/README.md`**
