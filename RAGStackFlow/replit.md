# RAG Document Chat - Replit Project

## Overview
Full-stack RAG (Retrieval Augmented Generation) application with Angular frontend and Python FastAPI backend. Users can upload documents (PDF, DOCX, XLSX, MD, TXT, CSV) and chat with them using Azure OpenAI with strict context grounding.

## Project Architecture

### Frontend (Angular 17 + Material Design)
- **Port**: 4200
- **Location**: `frontend/rag-app/`
- **Key Features**:
  - Drag-and-drop file upload component
  - Real-time chat interface with typing indicators
  - Source citations and confidence scores
  - Session management and reset

### Backend (Python FastAPI)
- **Port**: 8000
- **Location**: `backend/`
- **Key Components**:
  - `main.py`: FastAPI application with CORS
  - `rag_pipeline.py`: RAG implementation with LangChain
  - Document processing and embedding generation
  - FAISS vector store for similarity search
  - Azure OpenAI integration

### Data Storage
- **Uploads**: `data/uploads/`
- **Vector Store**: `data/vector_store/`
- **Format**: FAISS index with metadata

## Recent Changes

### 2025-01-17: Azure OpenAI Migration
- Migrated from OpenAI API to Azure OpenAI for better enterprise support
- Updated embeddings to use Azure OpenAI text-embedding-ada-002
- Integrated Azure OpenAI GPT-4o for chat responses
- Implemented few-shot prompting for improved response quality
- Enhanced RAG evaluation with similarity scoring and keyword matching
- Updated frontend port from 5000 to 4200 to avoid conflicts
- Optimized chunk size (1200 chars, 200 overlap) and retrieval parameters (6 chunks, fetch_k=15)

### 2025-10-12: Initial Implementation
- Set up Angular 17 frontend with Material Design
- Implemented Python FastAPI backend with LangChain
- Added FAISS vector store with MMR retrieval
- Added context grounding guardrails
- Created file upload component with drag-and-drop
- Built chat interface with source citations
- Configured concurrent workflows for frontend and backend

## Required API Keys

Set these in Replit Secrets:

1. **AZURE_OPENAI_API_KEY** (Required)
   - Your Azure OpenAI API key
   - Get from: Azure OpenAI resource in Azure Portal

2. **AZURE_OPENAI_ENDPOINT** (Required)
   - Your Azure OpenAI endpoint URL
   - Format: https://your-resource.openai.azure.com/

3. **AZURE_OPENAI_API_VERSION** (Required)
   - API version (e.g., "2024-02-01")

4. **AZURE_OPENAI_CHAT_DEPLOYMENT_NAME** (Required)
   - GPT-4o deployment name in your Azure OpenAI resource

5. **AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME** (Required)
   - text-embedding-ada-002 deployment name in your Azure OpenAI resource

## User Preferences

### Coding Style
- TypeScript/Angular: Standalone components, reactive patterns
- Python: Type hints, async/await for concurrency
- Clean, modular code with clear separation of concerns

### Workflow Preferences
- Automatic workflow restart after changes
- Console logs for backend debugging
- Webview for frontend development

## How to Use

1. **Start the Application**: 
   - Both workflows start automatically
   - Frontend: http://localhost:4200
   - Backend: http://localhost:8000

2. **Upload Documents**:
   - Drag & drop or select files
   - Supports: PDF, DOCX, XLSX, TXT, CSV, MD
   - Files are processed and indexed automatically

3. **Chat with Documents**:
   - Ask questions about uploaded documents
   - View source citations and confidence scores

4. **Reset Session**:
   - Click refresh button to clear chat history

## Technical Details

### RAG Pipeline
1. **Document Loading**: LangChain loaders for various formats
2. **Text Splitting**: RecursiveCharacterTextSplitter (1200 chars, 200 overlap)
3. **Embedding**: Azure OpenAI text-embedding-ada-002
4. **Storage**: FAISS vector store (IndexFlatIP for cosine similarity)
5. **Retrieval**: MMR for diverse results (top 6, fetch_k=15)
6. **Generation**: Azure OpenAI GPT-4o with few-shot prompting and conversation memory

### Context Grounding
- Responses ONLY from uploaded documents
- Guardrail chain rejects off-topic questions
- Hallucination detection prevents unsupported claims
- Source citations for transparency
- Confidence scores based on retrieval quality

### Frontend-Backend Integration
- CORS enabled for localhost development
- HTTP client for API communication
- Async operations for upload and chat
- Real-time updates with RxJS

## Troubleshooting

### Frontend not loading
- Check Frontend workflow is running on port 4200
- Verify Angular dev server is configured for 0.0.0.0:4200
- Check browser console for errors

### Backend errors
- Verify all Azure OpenAI environment variables are set in Secrets
- Check Backend workflow logs
- Visit `/health` endpoint to verify Azure OpenAI connection

### Chat errors
- Upload at least one document first
- Verify Azure OpenAI configuration is complete
- Check backend logs for Azure OpenAI API errors
