# 🔍 RAG Document Explorer

[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com)
[![LangChain](https://img.shields.io/badge/LangChain-0.3.7-orange.svg)](https://langchain.com)
[![Azure OpenAI](https://img.shields.io/badge/Azure%20OpenAI-GPT--4o-purple.svg)](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> A Retrieval-Augmented Generation (RAG) powered document search application built with LangChain, FAISS, and Azure OpenAI. Deploy on Replit in minutes!

![RAG Document Explorer Demo](https://img.shields.io/badge/Demo-Live%20on%20Replit-blueviolet)

---

## 📑 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Architecture](#️-architecture)
- [Technologies Used](#️-technologies-used)
- [Installation](#-installation)
- [Vector Stores Deep Dive](#️-vector-stores---deep-dive)
- [Why Replit?](#-why-replit)
- [License](#-license)

---

## 📋 Overview

**RAG Document Explorer** is a Retrieval-Augmented Generation (RAG) application that allows users to upload PDF documents, process them into a searchable vector database, and query them using natural language. The application leverages Azure OpenAI's GPT-4o for intelligent responses and text-embedding-ada-002 for semantic search capabilities.

### What is RAG?

RAG (Retrieval-Augmented Generation) is a technique that combines:
1. **Retrieval**: Finding relevant document chunks based on semantic similarity
2. **Augmentation**: Providing retrieved context to a Large Language Model (LLM)
3. **Generation**: LLM generates accurate answers grounded in the retrieved documents

This approach ensures responses are factual and based on your specific documents rather than the model's general training data.

---

## ✨ Features

- 📄 **PDF Upload** - Drag & drop or click to upload PDF documents
- 🔐 **Secure API Key** - Configure Azure OpenAI key via UI (masked after entry)
- 🧠 **Semantic Search** - Find relevant content using natural language queries
- 💬 **AI-Powered Answers** - Get intelligent responses from GPT-4o
- 📊 **Sample Questions** - Pre-built queries for quick testing
- 🗑️ **Clear Vector Store** - Reset knowledge base with one click
- ☁️ **Replit Ready** - Deploy and run on Replit instantly

---

## 🚀 Quick Start

### Option 1: Run on Replit (Recommended)

1. Upload the project as a ZIP to [Replit](https://replit.com)
2. Click the **Run** button
3. Enter your Azure OpenAI API key in the UI
4. Upload PDFs and start querying!

### Option 2: Run Locally

```bash
# Clone the repository
git clone https://github.com/yourusername/rag-document-explorer.git
cd rag-document-explorer

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open http://localhost:5000 in your browser
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (SPA)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  API Key    │  │  PDF Upload │  │  Query Interface        │  │
│  │  Config     │  │  Dropzone   │  │  + Sample Questions     │  │
│  └─────────────┘  └─────────────┘  └─────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                     Flask Backend (REST API)                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────────────┐ │
│  │/configure│  │ /ingest  │  │  /query  │  │ /load │ /clear   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                       RAG Engine (LangChain)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐  │
│  │  PDF Loader     │  │  Text Splitter  │  │  FAISS Vector   │  │
│  │  (PyPDF)        │  │  (Recursive)    │  │  Store          │  │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Azure OpenAI Services                       │
│  ┌─────────────────────────┐  ┌───────────────────────────────┐ │
│  │  text-embedding-ada-002 │  │  GPT-4o                       │ │
│  │  (Vector Embeddings)    │  │  (Response Generation)        │ │
│  └─────────────────────────┘  └───────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Technologies Used

### Backend
| Technology | Purpose |
|------------|---------|
| **Python 3.11** | Core programming language |
| **Flask** | Web framework for REST API |
| **LangChain** | RAG orchestration framework |
| **FAISS** | Vector similarity search library |
| **PyPDF** | PDF document parsing |

### Frontend
| Technology | Purpose |
|------------|---------|
| **HTML5** | Structure |
| **CSS3** | Styling with CSS variables, animations |
| **Vanilla JavaScript** | Interactivity, API communication |

### AI/ML Services
| Service | Model | Purpose |
|---------|-------|---------|
| **Azure OpenAI** | text-embedding-ada-002 | Convert text to vector embeddings |
| **Azure OpenAI** | GPT-4o | Generate natural language responses |

### Deployment
| Platform | Purpose |
|----------|---------|
| **Replit** | Cloud hosting and deployment |

---

## 🌐 Why Replit? - Cloud Development Platform

### What is Replit?

**Replit** is a cloud-based Integrated Development Environment (IDE) that allows developers to write, run, and deploy applications entirely in the browser. It eliminates the need for local setup, making it ideal for:

- 🎓 **Learning & Prototyping** - No installation required
- 🤝 **Collaboration** - Share and work together in real-time
- 🚀 **Instant Deployment** - Apps go live with one click
- 🌍 **Accessibility** - Code from any device with a browser

### Why We Chose Replit for This Project

| Benefit | Description |
|---------|-------------|
| **Zero Setup** | No need to install Python, pip, or configure environments locally |
| **Instant Preview** | See the web app running immediately in the browser |
| **Public URL** | Get a shareable URL to demo the application to others |
| **Persistent Storage** | Vector store persists between sessions |
| **Built-in Shell** | Run pip commands and debug directly |
| **Free Tier** | Deploy and run without cost (with limitations) |

### How Replit Works with Our RAG App

```
┌─────────────────────────────────────────────────────────────────┐
│                        REPLIT PLATFORM                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Browser-Based IDE                                        │  │
│  │  ├── File Editor (edit .py, .html, .css, .js)            │  │
│  │  ├── Shell Terminal (pip install, python app.py)          │  │
│  │  └── Preview Pane (live web app view)                     │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Replit Container (Linux VM)                              │  │
│  │  ├── Python 3.11 Runtime                                  │  │
│  │  ├── Flask Server (port 5000)                             │  │
│  │  ├── Installed Packages (.pythonlibs/)                    │  │
│  │  └── Project Files (rag-app/)                             │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│                              ▼                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Public URL: https://your-repl-name.username.repl.co      │  │
│  │  → Accessible by anyone on the internet                   │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### Replit-Specific Configurations

**`.replit` file** - Tells Replit how to run the app:
```toml
run = "python app.py"
entrypoint = "app.py"

[[ports]]
localPort = 5000
externalPort = 80
```

**`replit.nix`** - Specifies system packages:
```nix
{ pkgs }: {
  deps = [
    pkgs.python311
  ];
}
```

### Replit Limitations & Solutions

| Challenge | Solution |
|-----------|----------|
| **Disk Quota (Free Tier)** | Used minimal requirements.txt without heavy packages like PyTorch |
| **Memory Limits** | Azure OpenAI handles heavy computation, not the Replit container |
| **Cold Starts** | Vector store persists to disk, quick reload on restart |
| **No GPU** | Embeddings generated by Azure OpenAI API, not locally |

### Demo Workflow on Replit

1. **Upload Project** → Drag & drop zip file or upload files individually
2. **Install Dependencies** → `pip install -r requirements.txt` in Shell
3. **Run Application** → Click "Run" button or `python app.py`
4. **Access Preview** → Web app appears in preview pane
5. **Share URL** → Copy the public `.repl.co` URL to share with others
6. **Live Demo** → Configure API key, upload PDFs, query documents

### Why Replit is Perfect for RAG Demos

✅ **Immediate Results** - No "works on my machine" issues
✅ **Shareable** - Send URL to stakeholders for instant demo
✅ **Collaborative** - Multiple people can view/edit simultaneously
✅ **Cloud-Native** - Connects to Azure OpenAI seamlessly
✅ **Educational** - Students can fork and learn from the project

---

## 📁 Project Structure

```
rag-app/
├── app.py                 # Flask backend - REST API endpoints
├── rag_engine.py          # Core RAG logic with LangChain
├── config.py              # Configuration (Azure endpoints, settings)
├── requirements.txt       # Python dependencies
├── .replit                # Replit configuration
├── replit.nix             # Nix packages for Replit
├── static/
│   ├── index.html         # Single Page Application (SPA)
│   ├── style.css          # Modern dark theme styling
│   └── app.js             # Frontend JavaScript logic
├── pdfs/                  # (Optional) Default PDF directory
└── vector_store/          # FAISS index (created after ingestion)
```

---

## 🔄 How It Works

### 1. Document Ingestion Pipeline

```
PDF Files → PDF Loader → Text Chunks → Embeddings → Vector Store
```

**Step-by-step:**
1. User uploads PDF files via drag-and-drop
2. **PyPDFLoader** extracts text from each PDF page
3. **RecursiveCharacterTextSplitter** splits text into chunks (1000 chars, 200 overlap)
4. **Azure OpenAI Embeddings** converts each chunk to a 1536-dimensional vector
5. **FAISS** indexes vectors for fast similarity search
6. Vector store is saved to disk for persistence

### 2. Query Pipeline

```
Question → Embedding → Similarity Search → Context + Question → LLM → Answer
```

**Step-by-step:**
1. User enters a natural language question
2. Question is converted to embedding vector
3. **FAISS** finds top 4 most similar document chunks
4. Retrieved chunks are formatted as context
5. Context + question sent to **GPT-4o** with a prompt template
6. LLM generates a grounded, accurate response
7. Response + source documents returned to user

---

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve the SPA frontend |
| `/api/health` | GET | Check system status |
| `/api/configure` | POST | Set Azure OpenAI API key |
| `/api/ingest` | POST | Upload and ingest PDF files |
| `/api/query` | POST | Query the RAG system |
| `/api/load` | POST | Load existing vector store |
| `/api/clear` | POST | Delete vector store |

### Example API Usage

**Configure API Key:**
```bash
curl -X POST http://localhost:5000/api/configure \
  -H "Content-Type: application/json" \
  -d '{"api_key": "your-azure-openai-key"}'
```

**Query Documents:**
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What problem were GANs trying to solve?"}'
```

---

## ✨ Features

### User Interface
- 🎨 **Modern Dark Theme** - Azure-inspired color scheme
- 📱 **Responsive Design** - Works on desktop and mobile
- 🔐 **API Key Input** - Secure configuration with masked display
- 📄 **Drag & Drop Upload** - Easy PDF file upload
- 📋 **File Management** - View, remove uploaded files
- 💬 **Query Interface** - Natural language search
- 🏷️ **Sample Questions** - Pre-loaded example queries
- 📚 **Source Citations** - Shows which documents were used

### Backend Capabilities
- ⚡ **Fast Vector Search** - FAISS similarity search
- 💾 **Persistent Storage** - Vector store saved to disk
- 🔄 **Hot Reload** - Load existing stores without re-ingestion
- 🗑️ **Clear Store** - Delete and start fresh
- 📊 **Chunking Strategy** - Optimized text splitting

---

## 🚀 Setup & Deployment

### Local Development

```bash
# Navigate to project
cd rag-app

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py

# Open browser
open http://localhost:5000
```

### Replit Deployment

1. Create new Python project on Replit
2. Upload all files from `rag-app/` folder
3. In Shell, run:
   ```bash
   pip install -r requirements.txt
   python app.py
   ```
4. Enter your Azure OpenAI API key in the UI
5. Upload PDFs and start querying!

---

## 🔧 Configuration

### Azure OpenAI Settings (config.py)

```python
AZURE_OPENAI_ENDPOINT = "https://app-tx-peer.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-06-01"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
AZURE_OPENAI_CHAT_DEPLOYMENT = "gpt-4o"
```

### RAG Settings

```python
CHUNK_SIZE = 1000        # Characters per chunk
CHUNK_OVERLAP = 200      # Overlap between chunks
VECTOR_STORE_PATH = "vector_store"  # Save location
```

---

## 📚 Sample Use Case: AI Research Papers

This application was built to query a collection of landmark AI/ML research papers:

1. **Generative Adversarial Nets (GANs)** - Goodfellow et al., 2014
2. **Going Deeper with Convolutions (GoogLeNet)** - Szegedy et al., 2015
3. **Deep Residual Learning (ResNet)** - He et al., 2015
4. **Attention Is All You Need (Transformers)** - Vaswani et al., 2017
5. **Mercury: Ultra-Fast Diffusion Models** - 2024/2025
6. **SAM 2: Segment Anything** - 2025

### Example Queries

- "What problem were GANs trying to solve in AI?"
- "What is attention, and why did it replace older sequence models?"
- "How does ResNet fix the vanishing gradient problem?"
- "What makes Mercury models faster than older AI models?"
- "How does SAM 2 use memory for video segmentation?"

---

## 🧠 Key Concepts Explained

### Vector Embeddings
Text is converted to high-dimensional vectors (1536 dimensions) that capture semantic meaning. Similar concepts have similar vectors, enabling semantic search.

### LangChain Expression Language (LCEL)
Modern way to compose LangChain components:
```python
chain = prompt | llm | output_parser
result = chain.invoke({"context": ctx, "question": q})
```

### Chunking Strategy
Documents are split into overlapping chunks to:
- Fit within embedding model's context window
- Preserve context at chunk boundaries
- Enable granular retrieval

---

## 🗄️ Vector Stores - Deep Dive

### What is a Vector Store?

A **Vector Store** (also called Vector Database) is a specialized database designed to store, index, and search high-dimensional vectors efficiently. Unlike traditional databases that search by exact matches or keywords, vector stores find items based on **semantic similarity**.

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRADITIONAL DATABASE                         │
│  Query: "machine learning"                                      │
│  Result: Only documents containing exact phrase "machine learning" │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      VECTOR STORE                               │
│  Query: "machine learning"                                      │
│  Result: Documents about ML, AI, neural networks, deep learning │
│          (semantically similar, even without exact match)       │
└─────────────────────────────────────────────────────────────────┘
```

### How Vector Stores Work

```
                    INDEXING PHASE
┌──────────┐    ┌────────────────┐    ┌──────────────┐    ┌─────────────┐
│  Text    │ →  │  Embedding     │ →  │   Vector     │ →  │   Vector    │
│  Chunk   │    │  Model (API)   │    │  [0.1, 0.3,  │    │   Store     │
│          │    │                │    │   -0.2, ...] │    │   (Index)   │
└──────────┘    └────────────────┘    └──────────────┘    └─────────────┘

                    SEARCH PHASE
┌──────────┐    ┌────────────────┐    ┌──────────────┐    ┌─────────────┐
│  Query   │ →  │  Embedding     │ →  │   Query      │ →  │  Similarity │
│  Text    │    │  Model (API)   │    │   Vector     │    │   Search    │
└──────────┘    └────────────────┘    └──────────────┘    └─────────────┘
                                                                 │
                                                                 ▼
                                                          ┌─────────────┐
                                                          │  Top K Most │
                                                          │  Similar    │
                                                          │  Chunks     │
                                                          └─────────────┘
```

### FAISS - Our Vector Store Choice

**FAISS** (Facebook AI Similarity Search) is an open-source library developed by Meta AI for efficient similarity search and clustering of dense vectors.

#### Why FAISS?

| Feature | Benefit |
|---------|---------|
| **Speed** | Optimized algorithms for fast nearest-neighbor search |
| **Scalability** | Handles millions to billions of vectors |
| **Memory Efficient** | Various index types for different memory/speed trade-offs |
| **No Server Required** | Runs as a library, no separate database server |
| **Free & Open Source** | MIT licensed, no cost |
| **LangChain Integration** | Native support in LangChain framework |

#### How FAISS Works in Our App

```python
# 1. Create vector store from document chunks
vector_store = FAISS.from_documents(chunks, embeddings)

# 2. Save to disk for persistence
vector_store.save_local("vector_store")

# 3. Load existing store
vector_store = FAISS.load_local("vector_store", embeddings)

# 4. Search for similar documents
retriever = vector_store.as_retriever(search_kwargs={"k": 4})
similar_docs = retriever.invoke("What is attention?")
```

### Vector Similarity Explained

Vectors are compared using **cosine similarity** - measuring the angle between two vectors:

```
        Vector A (Document about GANs)
           ↗
          /
         /  θ = small angle = HIGH similarity
        /
       ●──────────→ Vector B (Query about "generative models")


        Vector A (Document about GANs)
           ↗
          /
         /
        /
       ●
        \
         \  θ = large angle = LOW similarity
          \
           ↘
             Vector C (Query about "cooking recipes")
```

**Cosine Similarity Formula:**
```
similarity = cos(θ) = (A · B) / (||A|| × ||B||)

- Value of 1.0 = Identical meaning
- Value of 0.0 = Unrelated
- Value of -1.0 = Opposite meaning
```

### Vector Store vs Traditional Database

| Aspect | Traditional DB (SQL) | Vector Store (FAISS) |
|--------|---------------------|---------------------|
| **Data Type** | Structured rows/columns | High-dimensional vectors |
| **Search Method** | Exact match, LIKE, regex | Semantic similarity |
| **Query** | `WHERE title = 'GANs'` | "papers about image generation" |
| **Index Type** | B-tree, Hash | IVF, HNSW, Flat |
| **Use Case** | Transactions, exact lookups | AI/ML, recommendations, search |

### Vector Store in RAG Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                        RAG PIPELINE                             │
│                                                                 │
│  ┌─────────┐                                                    │
│  │  PDFs   │                                                    │
│  └────┬────┘                                                    │
│       │                                                         │
│       ▼                                                         │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────────────┐ │
│  │ Text        │ →  │ Embedding   │ →  │ FAISS Vector Store  │ │
│  │ Splitter    │    │ Model       │    │ ┌─────────────────┐ │ │
│  │ (1000 chars)│    │ (ada-002)   │    │ │ [0.1, 0.2, ...]│ │ │
│  └─────────────┘    └─────────────┘    │ │ [0.3, -0.1, ...]│ │ │
│                                        │ │ [0.5, 0.4, ...] │ │ │
│                                        │ │ ... (N chunks)  │ │ │
│                                        │ └─────────────────┘ │ │
│                                        └──────────┬──────────┘ │
│                                                   │             │
│  ┌─────────────┐    ┌─────────────┐              │             │
│  │ User Query  │ →  │ Query       │ ─────────────┘             │
│  │ "What is    │    │ Embedding   │     Similarity              │
│  │  attention?"│    │ [0.4, 0.3..]│     Search                  │
│  └─────────────┘    └─────────────┘         │                   │
│                                             ▼                   │
│                                    ┌─────────────────┐          │
│                                    │ Top 4 Similar   │          │
│                                    │ Document Chunks │          │
│                                    └────────┬────────┘          │
│                                             │                   │
│                                             ▼                   │
│                                    ┌─────────────────┐          │
│                                    │ GPT-4o + Context│          │
│                                    │ → Generate      │          │
│                                    │   Answer        │          │
│                                    └─────────────────┘          │
└─────────────────────────────────────────────────────────────────┘
```

### Our Vector Store Configuration

```python
# config.py settings
VECTOR_STORE_PATH = "vector_store"  # Directory to save index
CHUNK_SIZE = 1000                    # Characters per chunk
CHUNK_OVERLAP = 200                  # Overlap for context continuity
```

**What gets saved in `vector_store/` directory:**
```
vector_store/
├── index.faiss    # The actual FAISS index (binary)
└── index.pkl      # Metadata and document mappings (pickle)
```

### Popular Vector Stores Comparison

| Vector Store | Type | Best For | Used In |
|--------------|------|----------|---------|
| **FAISS** | Library | Local apps, prototypes | ✅ This project |
| **Pinecone** | Cloud Service | Production, managed | Enterprise apps |
| **Chroma** | Library/Server | Development, testing | Prototypes |
| **Weaviate** | Self-hosted | Custom deployments | On-premise |
| **Milvus** | Distributed | Large scale | Big data AI |
| **pgvector** | PostgreSQL extension | Existing Postgres users | Hybrid apps |

### Why FAISS for This Project?

1. **No External Service** - Runs entirely within Replit
2. **No API Keys** - Unlike Pinecone, no additional credentials
3. **Persistent** - Saves to disk, survives restarts
4. **Fast Enough** - For demo/prototype scale (thousands of chunks)
5. **LangChain Native** - First-class support in LangChain

---

## 📝 License

MIT License - Feel free to use and modify for your projects.

---

## 🙏 Credits

| Technology | Role | Website |
|------------|------|---------|
| **LangChain** | RAG orchestration framework | [langchain.com](https://langchain.com) |
| **Azure OpenAI** | GPT-4o & Embeddings API | [azure.microsoft.com](https://azure.microsoft.com/en-us/products/ai-services/openai-service) |
| **FAISS** | Vector similarity search | [github.com/facebookresearch/faiss](https://github.com/facebookresearch/faiss) |
| **Replit** | Cloud IDE & deployment platform | [replit.com](https://replit.com) |
| **Flask** | Python web framework | [flask.palletsprojects.com](https://flask.palletsprojects.com) |

---

## 🎯 Summary

This project demonstrates a complete **RAG (Retrieval-Augmented Generation)** pipeline:

1. **Built** a full-stack web application with Flask backend and modern SPA frontend
2. **Integrated** Azure OpenAI for embeddings (text-embedding-ada-002) and chat (GPT-4o)
3. **Implemented** document ingestion with PDF parsing and intelligent chunking
4. **Created** a vector database using FAISS for semantic search
5. **Deployed** on Replit for instant cloud access and easy demonstrations
6. **Designed** an intuitive UI with drag-and-drop uploads and real-time querying

The combination of **LangChain** for RAG logic, **Azure OpenAI** for AI capabilities, and **Replit** for deployment creates a powerful, accessible, and demonstrable AI application.

---

*Built with ❤️ using RAG, LangChain, Azure OpenAI & Replit*

