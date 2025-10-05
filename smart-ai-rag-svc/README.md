# Smart AI RAG Service

A production-ready Retrieval-Augmented Generation (RAG) service built with **LangChain**, **LlamaIndex**, **OpenAI**, and **MongoDB Vector Search**. Features dual framework support, professional AI responses, and quality evaluation.

## 🚀 Features

- **Dual Framework Support**: Switch between LangChain and LlamaIndex for document processing and retrieval
- **Professional AI Responses**: Direct, concise answers without unnecessary politeness
- **PDF Processing**: Automatic document loading and intelligent chunking
- **Vector Storage**: MongoDB Atlas Vector Search for semantic similarity
- **Quality Evaluation**: TruLens-powered RAG evaluation (answer relevance, context relevance, groundedness)
- **Conversation History**: Maintain context across follow-up questions
- **REST API**: Production-ready FastAPI service with comprehensive endpoints
- **Error Resilience**: Robust error handling with clear, actionable messages

## 📋 Table of Contents

- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [RAG Quality Evaluation](#rag-quality-evaluation)
- [Framework Comparison](#framework-comparison-llamaindex-vs-langchain)
- [Examples](#examples)
- [Troubleshooting](#troubleshooting)

---

## Quick Start

```bash
# 1. Clone and setup
git clone <repository-url>
cd smart-ai-rag-svc
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure environment
cp env_template .env
# Edit .env with your OPENAI_API_KEY and MONGODB_URI

# 3. Setup MongoDB index
python scripts/setup_mongodb_index.py

# 4. Start service
python main.py

# 5. Upload a document
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=true" \
  -F "file=@your_document.pdf"

# 6. Ask a question
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is this document about?"}'
```

---

## Installation

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account (free tier works)
- OpenAI API key

### Step-by-Step Installation

#### 1. Clone the repository
   ```bash
   git clone <repository-url>
cd smart-ai-rag-svc
   ```

#### 2. Create a virtual environment
   ```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Linux/Mac
# OR
venv\Scripts\activate  # On Windows
```

#### 3. Install dependencies
   ```bash
   pip install -r requirements.txt
   ```

#### 4. Set up environment variables
   ```bash
   cp env_template .env
   ```
   
   Edit `.env` file with your configuration:
   ```env
   # OpenAI Configuration
OPENAI_API_KEY=sk-your-openai-api-key-here
OPENAI_EMBEDDING_MODEL=text-embedding-ada-002
OPENAI_LLM_MODEL=gpt-3.5-turbo
   
# MongoDB Configuration (MongoDB Atlas)
   MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
   MONGODB_DATABASE=rag_database
   MONGODB_COLLECTION=documents
MONGODB_VECTOR_INDEX=vector_index

# RAG Configuration
CHUNK_SIZE=500                     # LangChain chunk size
CHUNK_OVERLAP=100                  # LangChain overlap
SENTENCE_WINDOW_SIZE=3             # LlamaIndex window size (sentences before/after)
TOP_K_RESULTS=5                    # Number of chunks to retrieve
SIMILARITY_THRESHOLD=0.7           # Minimum similarity score
MAX_TOKENS=1000                    # LLM max tokens
TEMPERATURE=0.1                    # LLM temperature (0 = deterministic)
```

#### 5. Set up MongoDB Vector Search Index

**IMPORTANT**: You must create a vector search index in MongoDB Atlas before uploading documents.

   ```bash
   python scripts/setup_mongodb_index.py
   ```

This will create an index with the following configuration:
- **Field**: `embedding`
- **Dimensions**: 1536 (for text-embedding-ada-002)
- **Similarity**: cosine

Alternatively, create it manually in MongoDB Atlas:
1. Go to your cluster → Browse Collections → Search Indexes
2. Create Search Index → JSON Editor
3. Use the configuration from `scripts/setup_mongodb_index.py`

#### 6. Start the service
```bash
python main.py
```

The service will start at `http://localhost:8000`

**Check health:**
```bash
curl http://localhost:8000/health
# Should return: {"status":"healthy","timestamp":"...","version":"1.0.0"}
```

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | Your OpenAI API key | - | ✅ Yes |
| `OPENAI_EMBEDDING_MODEL` | Embedding model | `text-embedding-ada-002` | No |
| `OPENAI_LLM_MODEL` | Language model | `gpt-3.5-turbo` | No |
| `MONGODB_URI` | MongoDB connection string | - | ✅ Yes |
| `MONGODB_DATABASE` | Database name | `rag_database` | No |
| `MONGODB_COLLECTION` | Collection name | `documents` | No |
| `MONGODB_VECTOR_INDEX` | Vector index name | `vector_index` | No |
| `CHUNK_SIZE` | LangChain chunk size | `500` | No |
| `CHUNK_OVERLAP` | LangChain overlap | `100` | No |
| `SENTENCE_WINDOW_SIZE` | LlamaIndex window size | `3` | No |
| `TOP_K_RESULTS` | Results to retrieve | `5` | No |
| `SIMILARITY_THRESHOLD` | Min similarity score | `0.7` | No |
| `MAX_TOKENS` | LLM max tokens | `1000` | No |
| `TEMPERATURE` | LLM temperature | `0.1` | No |

### Configuration Notes

1. **NEVER set environment variables in your shell** (export commands) - use `.env` file only
2. **Chunk Size**: Lower values (500) = more precise, Higher values (1500) = more context
3. **Sentence Window**: Number of sentences before/after each chunk (LlamaIndex only)
4. **Top K**: More results = more context but slower and potentially less relevant
5. **Temperature**: 0 = deterministic, 1 = creative (recommend 0.1 for factual answers)

---

## Usage

### 1. Upload Documents

**Option A: Upload with LlamaIndex (Recommended)**
```bash
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=true" \
  -F "file=@/path/to/document.pdf"
```

**Option B: Upload with LangChain**
```bash
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=false" \
  -F "file=@/path/to/document.pdf"
```

**Response:**
```json
{
  "success": true,
  "message": "Successfully indexed 2 documents with 4 nodes using LlamaIndex",
  "document_stats": {
    "total_documents": 2,
    "total_nodes": 4,
    "total_characters": 2893
  },
  "original_filename": "document.pdf"
}
```

### 2. Ask Questions

**Basic Query:**
```bash
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
     -H "Content-Type: application/json" \
  -d '{
    "question": "What is the main topic of this document?",
    "k": 5
  }'
```

**Response:**
```json
{
  "answer": "The main topic is machine learning applications.",
  "sources": [
    {
      "chunk_id": 0,
      "content_preview": "Machine learning is...",
      "metadata": {...},
      "score": 0.92
    }
  ],
  "num_sources": 3,
  "processing_time": 1.25,
  "timestamp": "2025-10-05T12:00:00",
  "query_engine": "llamaindex"
}
```

### 3. Evaluate Quality

```bash
curl -X POST "http://localhost:8000/evaluate/query" \
     -H "Content-Type: application/json" \
     -d '{
    "question": "What are the key findings?",
    "use_llamaindex": true
     }'
```

**Response:**
```json
{
  "rag_response": {
    "answer": "The key findings are...",
    "num_sources": 3
  },
  "evaluation": {
    "metrics": {
      "answer_relevance": 1.0,
      "context_relevance": 0.85,
      "groundedness": 0.95,
      "overall_quality": 0.93
    }
  },
  "summary": {
    "quality_assessment": {
      "level": "excellent",
      "message": "Excellent quality response!"
    },
    "recommendations": [...]
  }
}
```

---

## API Endpoints

### Document Management

#### Upload Document
```http
POST /documents/upload-file?use_llamaindex=true
Content-Type: multipart/form-data

file: <PDF file>
```

**Parameters:**
- `use_llamaindex` (query): `true` for LlamaIndex, `false` for LangChain

#### Get Service Stats
```http
GET /stats
```

Returns configuration and document count.

---

### Question Answering

#### Ask Question
```http
POST /questions/ask?use_llamaindex=true
Content-Type: application/json

{
  "question": "Your question here",
  "k": 5,
  "use_conversation_history": false
}
```

**Parameters:**
- `use_llamaindex` (query): Processor to use
- `k` (body): Number of chunks to retrieve (default: 5)
- `use_conversation_history` (body): Include conversation context

---

### Quality Evaluation

#### Evaluate Query (Recommended)
```http
POST /evaluate/query
Content-Type: application/json

{
  "question": "Your question",
  "use_llamaindex": true,
  "k": 5
}
```

Gets answer AND evaluation in one call.

#### Evaluate Existing Response
```http
POST /evaluate/rag
Content-Type: application/json

{
  "question": "...",
  "answer": "...",
  "context": ["chunk1", "chunk2"],
  "source_info": [...]
}
```

---

### Conversation Management

#### Get Conversation History
```http
GET /conversation/history
```

#### Clear Conversation History
```http
DELETE /conversation/history
```

---

### Health Check

#### Check Service Health
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-05T12:00:00.000000",
  "version": "1.0.0"
}
```

---

## RAG Quality Evaluation

### Metrics Explained

| Metric | Range | Description |
|--------|-------|-------------|
| **Answer Relevance** | 0-1 | Does the answer address the question? |
| **Context Relevance** | 0-1 | Are retrieved chunks relevant to the question? |
| **Groundedness** | 0-1 | Is the answer supported by the context? (no hallucination) |
| **Overall Quality** | 0-1 | Weighted average of all metrics |

### Quality Levels

- **Excellent** (0.8-1.0): Production-ready response
- **Good** (0.6-0.8): Acceptable with minor improvements
- **Fair** (0.4-0.6): Needs improvement
- **Poor** (0.0-0.4): Requires significant fixes

### Using Evaluation Results

**Good Response Example:**
```json
{
  "metrics": {
    "answer_relevance": 1.0,
    "context_relevance": 0.9,
    "groundedness": 1.0,
    "overall_quality": 0.97
  },
  "summary": {
    "quality_assessment": {
      "level": "excellent",
      "message": "Excellent quality response!"
    }
  }
}
```

**Improvement Needed:**
```json
{
  "metrics": {
    "answer_relevance": 0.3,
    "context_relevance": 0.2,
    "groundedness": 0.5,
    "overall_quality": 0.33
  },
  "recommendations": [
    {
      "issue": "Low Context Relevance",
      "solutions": [
        "Increase k (retrieve more chunks)",
        "Lower similarity threshold",
        "Improve document chunking"
      ]
    }
  ]
}
```

---

## Framework Comparison: LlamaIndex vs LangChain

### When to Use Each

#### Use **LlamaIndex** when:
- ✅ You need advanced retrieval strategies
- ✅ Processing complex, structured documents
- ✅ Want better metadata handling
- ✅ Need sentence-level precision

#### Use **LangChain** when:
- ✅ You prefer simpler, straightforward chunking
- ✅ Need maximum compatibility with existing tools
- ✅ Want basic, reliable document processing

### Technical Comparison

| Feature | LlamaIndex | LangChain |
|---------|-----------|-----------|
| **Chunking** | Sentence-based with window | Character-based with overlap |
| **Context** | Window context (3 sentences) | Fixed chunk size (500 chars) |
| **Metadata** | Rich metadata with windows | Basic metadata |
| **API** | Modern, non-deprecated | Stable, widely used |
| **Performance** | Slightly slower, better quality | Faster, good quality |

### Response Quality

Both processors produce **professional, concise answers**:

```
Question: "How many years of experience does John have?"

LlamaIndex: "John has 8 years of experience."
LangChain:  "John has 8 years of experience."
```

No more chatty responses like *"Based on the context, I can see that..."*

---

## Examples

### Python Examples

#### 1. Quick Start (`examples/quickstart.py`)
```python
import requests

# Upload document
files = {'file': open('document.pdf', 'rb')}
response = requests.post(
    'http://localhost:8000/documents/upload-file?use_llamaindex=true',
    files=files
)

# Ask question
response = requests.post(
    'http://localhost:8000/questions/ask?use_llamaindex=true',
    json={'question': 'What is this about?', 'k': 5}
)
print(response.json()['answer'])
```

#### 2. Compare Frameworks (`examples/compare_frameworks.py`)
Side-by-side comparison of LlamaIndex vs LangChain.

#### 3. Full Usage (`examples/example_usage.py`)
Complete demonstration of all features including evaluation.

### Quick cURL Examples

```bash
# 1. Upload document
curl -X POST "http://localhost:8000/documents/upload-file?use_llamaindex=true" \
  -F "file=@document.pdf"

# 2. Ask question
curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is the main topic?", "k": 5}'

# 3. Evaluate quality
curl -X POST "http://localhost:8000/evaluate/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the key points?", "use_llamaindex": true}'

# 4. Get service stats
curl http://localhost:8000/stats

# 5. Clear conversation
curl -X DELETE http://localhost:8000/conversation/history
```

---

## Troubleshooting

### Common Issues and Solutions

#### 1. "No documents indexed" Error

**Problem:**
```json
{
  "error": "No documents indexed with LlamaIndex. Upload documents with use_llamaindex=true or query with use_llamaindex=false."
}
```

**Solution:**
- Upload documents with the **same processor** you're querying with
- If you uploaded with `use_llamaindex=true`, query with `use_llamaindex=true`
- If you uploaded with `use_llamaindex=false`, query with `use_llamaindex=false`

#### 2. MongoDB Connection Error

**Problem:**
```
Failed to connect to MongoDB
```

**Solution:**
1. Check your `MONGODB_URI` in `.env`
2. Verify MongoDB Atlas allows connections from your IP
3. Ensure vector search index is created (run `scripts/setup_mongodb_index.py`)

#### 3. OpenAI API Error

**Problem:**
```
OpenAI API key not found
```

**Solution:**
1. Check `OPENAI_API_KEY` in `.env` file
2. **NEVER** set it via `export` command
3. Restart the service after updating `.env`

#### 4. KeyError: 'metadata'

**Problem:**
```json
{
  "error": "KeyError: 'metadata'"
}
```

**Solution:**
This happens when documents were indexed with one processor but queried with another. **Clear MongoDB and re-upload:**

```bash
# Clear all documents
python3 << 'EOF'
from pymongo import MongoClient
from decouple import config

client = MongoClient(config('MONGODB_URI'))
db = client['rag_database']
db['documents'].delete_many({})
client.close()
print("✅ Database cleared")
EOF

# Restart service and re-upload documents
python main.py
```

#### 5. Service Not Starting

**Problem:**
```
ModuleNotFoundError: No module named 'fastapi'
```

**Solution:**
1. Activate virtual environment: `source venv/bin/activate`
2. Install dependencies: `pip install -r requirements.txt`
3. Start service: `python main.py`

#### 6. Low Quality Scores

**Problem:**
```json
{
  "overall_quality": 0.35
}
```

**Solution:**
1. **Increase k**: Try `k=10` instead of `k=3` to retrieve more context
2. **Lower similarity threshold**: Set `SIMILARITY_THRESHOLD=0.5` in `.env`
3. **Check document quality**: Ensure PDFs have clear, extractable text
4. **Note**: Some low scores may be due to TruLens evaluation bugs, not actual quality issues

#### 7. Wrong Answers Despite Correct Documents

**Problem:**
Answer says "12 years" but actual experience is "17 years"

**Solution:**
1. **Increase k parameter**: More chunks = more complete information
   ```bash
   curl -X POST "http://localhost:8000/questions/ask?use_llamaindex=true" \
     -H "Content-Type: application/json" \
     -d '{"question": "...", "k": 10}'  # Instead of k=3
   ```

2. **Ask more specific questions**:
   - Bad: "How much experience?"
   - Good: "What is the TOTAL years of experience across ALL positions?"

3. **Use conversation history** for follow-ups:
   ```json
   {
     "question": "List all work experience with dates",
     "use_conversation_history": true,
     "k": 10
   }
   ```

---

## System Requirements

- **Python**: 3.8 or higher
- **RAM**: Minimum 2GB, 4GB recommended
- **Disk**: 500MB for dependencies + storage for documents
- **Network**: Internet access for OpenAI API and MongoDB Atlas

---

## Environment Setup Checklist

Before starting the service, verify:

- [ ] Virtual environment created and activated
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file created with valid credentials
- [ ] MongoDB Atlas vector search index created
- [ ] MongoDB allows connections from your IP
- [ ] OpenAI API key is valid and has credits
- [ ] **NO environment variables set in shell** (no `export` commands)

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP REST API
┌──────▼──────────────────────────────┐
│         FastAPI Service              │
│  ┌────────────────────────────────┐ │
│  │   EnhancedRAGService           │ │
│  │  ┌──────────┐  ┌─────────────┐ │ │
│  │  │LlamaIndex│  │ LangChain   │ │ │
│  │  │Processor │  │ Processor   │ │ │
│  │  └──────────┘  └─────────────┘ │ │
│  │  ┌──────────────────────────┐  │ │
│  │  │   RAGEvaluator (TruLens) │  │ │
│  │  └──────────────────────────┘  │ │
│  └────────────────────────────────┘ │
└──────┬──────────────┬───────────────┘
       │              │
┌──────▼──────┐  ┌───▼────────┐
│  MongoDB    │  │  OpenAI    │
│  Vector     │  │  API       │
│  Search     │  │            │
└─────────────┘  └────────────┘
```

---

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

## License

[Your License Here]

---

## Support

For issues or questions:
- Open a GitHub issue
- Check the [Troubleshooting](#troubleshooting) section
- Review the [Examples](#examples)

---

## Version History

### v1.0.0 (Current)
- ✅ Dual framework support (LlamaIndex + LangChain)
- ✅ Professional AI responses (no chatty answers)
- ✅ TruLens quality evaluation
- ✅ MongoDB Vector Search integration
- ✅ Comprehensive error handling
- ✅ Production-ready REST API
- ✅ Conversation history support
- ⚠️ Sentence Window Retrieval (parsing active, replacement temporarily disabled)

---

**Built with ❤️ for production RAG applications**
