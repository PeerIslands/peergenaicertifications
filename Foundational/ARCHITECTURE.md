# QueryMind AI Architecture

This document describes the architecture of the QueryMind AI system, which consists of two main components: **QueryMindAI** (web application) and **QueryMindIngestion** (PDF ingestion tool).

## System Overview

QueryMind AI is a RAG (Retrieval-Augmented Generation) powered chatbot that uses LLM and vector search to answer questions based on ingested PDF documents.

## Architecture Diagram

![QueryMindAI RAG Integration Architecture](./QueryMindAI%20RAG%20Integration%20architecture%20diagram.png)

*Visual architecture diagram showing the complete system integration*

### Interactive Diagram (Mermaid)

```mermaid

graph TB
    subgraph "User Interface"
        UI[React Frontend<br/>TypeScript/React]
    end

    subgraph "QueryMindAI - Web Application"
        subgraph "Client Layer"
            Client[React Client<br/>Chat Interface<br/>Analytics Dashboard]
        end
        
        subgraph "Server Layer"
            Express[Express Server<br/>TypeScript/Node.js]
            Routes[API Routes<br/>/api/chat<br/>/api/rag/search<br/>/api/health]
        end
        
        subgraph "Application Services"
            LangChain[LangChain Service<br/>LLM Integration]
            RAG[RAG Service<br/>Hybrid Search<br/>RRF Fusion]
            Embeddings[Embeddings Service<br/>Query Embeddings]
            MongoDBService[MongoDB Service<br/>Vector Search<br/>Atlas Search]
        end
        
        subgraph "Storage"
            PostgreSQL[(PostgreSQL<br/>Conversations<br/>Messages<br/>Analytics)]
        end
    end

    subgraph "QueryMindIngestion - PDF Processing"
        subgraph "Ingestion Pipeline"
            PDFReader[PDF Reader<br/>PyPDF2]
            TextChunker[Text Chunker<br/>LangChain<br/>RecursiveCharacterTextSplitter]
            MongoDBClient[MongoDB Client<br/>Document Storage]
            EmbeddingGen[Embedding Generator<br/>Ollama Integration]
        end
        
        PDFs[PDF Files<br/>./pdfs/]
    end

    subgraph "External Services"
        MongoDB[(MongoDB Atlas<br/>Vector Store<br/>Knowledge Base<br/>Embeddings)]
        Ollama[Ollama<br/>Local Embedding Model<br/>embeddinggemma]
        AzureOpenAI[Azure OpenAI<br/>GPT-4o-mini<br/>LLM Generation]
    end

    %% User interactions
    UI -->|HTTP Requests| Express
    Express -->|API Calls| Routes
    
    %% QueryMindAI flow
    Routes -->|Chat Request| LangChain
    LangChain -->|Retrieve Context| RAG
    RAG -->|Semantic Search| MongoDBService
    RAG -->|Keyword Search| MongoDBService
    RAG -->|Generate Embedding| Embeddings
    Embeddings -->|API Call| Ollama
    MongoDBService -->|Query| MongoDB
    LangChain -->|Generate Response| AzureOpenAI
    Routes -->|Store Data| PostgreSQL
    
    %% Ingestion flow
    PDFs -->|Read| PDFReader
    PDFReader -->|Extract Text| TextChunker
    TextChunker -->|Create Chunks| MongoDBClient
    MongoDBClient -->|Store Documents| MongoDB
    MongoDBClient -->|Request Embeddings| EmbeddingGen
    EmbeddingGen -->|API Call| Ollama
    EmbeddingGen -->|Update Documents| MongoDBClient
    MongoDBClient -->|Update with Embeddings| MongoDB

    %% Styling
    classDef frontend fill:#e1f5ff,stroke:#01579b,stroke-width:2px
    classDef backend fill:#f3e5f5,stroke:#4a148c,stroke-width:2px
    classDef service fill:#e8f5e9,stroke:#1b5e20,stroke-width:2px
    classDef storage fill:#fff3e0,stroke:#e65100,stroke-width:2px
    classDef external fill:#fce4ec,stroke:#880e4f,stroke-width:2px
    classDef ingestion fill:#e0f2f1,stroke:#004d40,stroke-width:2px

    class UI,Client frontend
    class Express,Routes backend
    class LangChain,RAG,Embeddings,MongoDBService service
    class PostgreSQL storage
    class MongoDB,Ollama,AzureOpenAI external
    class PDFReader,TextChunker,MongoDBClient,EmbeddingGen,PDFs ingestion
```

## Component Details

### QueryMindAI - Web Application

#### Frontend (Client)
- **Technology**: React, TypeScript, Vite
- **Components**:
  - Chat interface with message bubbles
  - Analytics dashboard
  - Theme toggle (dark/light mode)
  - Real-time typing indicators
- **Location**: `QueryMindAI/client/`

#### Backend (Server)
- **Technology**: Express.js, TypeScript, Node.js
- **Key Services**:
  - **LangChain Service**: Integrates with Azure OpenAI for LLM generation
  - **RAG Service**: Implements hybrid search combining:
    - Semantic search (vector similarity using embeddings)
    - Keyword search (MongoDB Atlas Search with BM25)
    - Reciprocal Rank Fusion (RRF) to combine results
  - **Embeddings Service**: Generates query embeddings using Ollama
  - **MongoDB Service**: Performs vector similarity search and Atlas Search
- **API Endpoints**:
  - `POST /api/chat` - Chat with RAG enhancement
  - `GET /api/rag/search` - Search knowledge base
  - `GET /api/rag/status` - Check RAG service status
  - `GET /api/health` - Health check
  - `GET /api/conversation/:id` - Get conversation history
  - `GET /api/analytics/:sessionId` - Get session analytics
- **Location**: `QueryMindAI/server/`

#### Storage
- **PostgreSQL**: Stores conversations, messages, and analytics data
- **MongoDB Atlas**: Vector store for knowledge base documents with embeddings

### QueryMindIngestion - PDF Processing Tool

#### Components
- **PDF Reader**: Extracts text from PDF files using PyPDF2
- **Text Chunker**: Splits PDF text into chunks using LangChain's RecursiveCharacterTextSplitter
- **MongoDB Client**: Stores chunked documents in MongoDB
- **Embedding Generator**: Generates embeddings for each chunk using Ollama's embeddinggemma model

#### Processing Flow
1. Read PDF files from `./pdfs/` directory
2. Extract text content from each PDF
3. Chunk text into manageable pieces (configurable chunk size and overlap)
4. Store chunks as documents in MongoDB
5. Generate embeddings for each chunk using Ollama
6. Update MongoDB documents with embeddings

#### Location: `QueryMindIngestion/`

## Data Flow

### Chat Flow (Query Time)
1. User sends message via React frontend
2. Express server receives request at `/api/chat`
3. RAG service generates query embedding using Ollama
4. RAG service performs hybrid search:
   - Semantic search: Vector similarity in MongoDB
   - Keyword search: BM25 search via MongoDB Atlas Search
   - Combine results using Reciprocal Rank Fusion
5. Retrieved context is passed to LangChain service
6. LangChain service calls Azure OpenAI with context + conversation history
7. Response is returned to user with source attribution
8. Conversation is stored in PostgreSQL

### Ingestion Flow (Indexing Time)
1. PDF files are placed in `./pdfs/` directory
2. PDF Reader extracts text from each PDF
3. Text Chunker splits text into semantic chunks
4. Chunks are stored in MongoDB as documents
5. Embedding Generator creates embeddings for each chunk using Ollama
6. MongoDB documents are updated with embedding vectors
7. MongoDB indexes are created for efficient search

## Technology Stack

### QueryMindAI
- **Frontend**: React, TypeScript, Vite, Tailwind CSS
- **Backend**: Express.js, TypeScript, Node.js
- **AI/ML**: LangChain, Azure OpenAI, Ollama
- **Database**: PostgreSQL (conversations), MongoDB Atlas (vector store)
- **Vector Search**: MongoDB aggregation pipeline (cosine similarity), MongoDB Atlas Search (BM25)

### QueryMindIngestion
- **Language**: Python 3.8+
- **Libraries**: LangChain, PyPDF2, PyMongo, Ollama client
- **Embedding Model**: embeddinggemma (via Ollama)

## External Dependencies

1. **MongoDB Atlas**: Cloud-hosted MongoDB for vector storage
   - Stores knowledge base documents with embeddings
   - Supports vector similarity search and Atlas Search

2. **Ollama**: Local embedding generation service
   - Model: `embeddinggemma`
   - Used by both ingestion and query services

3. **Azure OpenAI**: Cloud LLM service
   - Model: GPT-4o-mini
   - Used for generating chat responses

## Key Features

- **Hybrid Search**: Combines semantic (vector) and keyword (BM25) search
- **Reciprocal Rank Fusion**: Intelligently merges results from multiple search methods
- **Source Attribution**: Provides transparency by showing which documents were used
- **Conversation Management**: Maintains conversation history in PostgreSQL
- **Analytics**: Tracks message counts, response times, and conversation metrics
- **Real-time UI**: Typing indicators and responsive chat interface

## Configuration

Both components use environment variables for configuration:

### QueryMindAI
- `MONGODB_URI`: MongoDB connection string
- `AZURE_OPENAI_API_KEY`: Azure OpenAI API key
- `AZURE_OPENAI_ENDPOINT`: Azure OpenAI endpoint
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)
- `PORT`: Server port (default: 5000)

### QueryMindIngestion
- `PDF_FOLDER_PATH`: Path to PDF files directory
- `MONGODB_URI`: MongoDB connection string
- `MONGODB_DATABASE`: Database name
- `MONGODB_COLLECTION`: Collection name
- `OLLAMA_BASE_URL`: Ollama server URL
- `CHUNK_SIZE`: Text chunk size (default: 1000)
- `CHUNK_OVERLAP`: Chunk overlap size (default: 200)

