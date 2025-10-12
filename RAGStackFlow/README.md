# RAG Document Chat Application

A full-stack RAG (Retrieval Augmented Generation) application that allows users to upload documents and chat with them using Azure OpenAI with strict context grounding.

## Features

- **Multi-format Document Support**: Upload PDF, DOCX, XLSX, TXT, CSV, and Markdown files
- **Drag-and-Drop Upload**: Intuitive file upload interface
- **Azure OpenAI Integration**: Uses GPT-4o for chat and text-embedding-ada-002 for embeddings
- **Context Grounding**: Responses are strictly grounded in uploaded documents
- **Guardrails**: Automatically rejects off-topic questions and prevents hallucinations
- **Source Citations**: Every answer includes source files and confidence scores
- **Conversation Memory**: Maintains context across chat sessions
- **Vector Search**: Uses Azure OpenAI embeddings with FAISS for efficient similarity search
- **MMR Retrieval**: Maximum Marginal Relevance for diverse, relevant results

## Tech Stack

### Frontend
- **Angular 17** with Material Design
- Responsive layout with drag-and-drop file upload
- Real-time chat interface with typing indicators
- Session management

### Backend
- **Python FastAPI** with async endpoints
- **LangChain** for RAG pipeline
- **Azure OpenAI** for embeddings (text-embedding-ada-002) and chat (GPT-4o)
- **FAISS** vector store for fast similarity search
- Document loaders for PDF, DOCX, XLSX, TXT, CSV, MD

## Setup Instructions

### Prerequisites

1. **Azure OpenAI API Keys Required**:
   - `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
   - `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
   - `AZURE_OPENAI_API_VERSION` - API version (e.g., "2024-02-01")
   - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME` - GPT-4o deployment name
   - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME` - text-embedding-ada-002 deployment name

### Installation

The project is pre-configured to run on Replit with both servers starting automatically:

1. **Set Azure OpenAI Keys**: Click the "Secrets" tab and add your Azure OpenAI configuration:
   - `AZURE_OPENAI_API_KEY`
   - `AZURE_OPENAI_ENDPOINT`
   - `AZURE_OPENAI_API_VERSION`
   - `AZURE_OPENAI_CHAT_DEPLOYMENT_NAME`
   - `AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME`

2. **Run the Application**: The workflows will automatically start:
   - Frontend: http://localhost:4200 (Angular dev server)
   - Backend: http://localhost:8000 (FastAPI server)

3. **Open the App**: Click the webview to access the application

### Local Development

If running locally:

#### Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```

#### Frontend
```bash
cd frontend/rag-app
npm install
npm start
```

## Usage

1. **Upload Documents**:
   - Drag and drop files or click "Select Files"
   - Supported formats: PDF, DOCX, XLSX, TXT, CSV, MD
   - Files are automatically processed and indexed

2. **Chat with Documents**:
   - Ask questions about your uploaded documents
   - Responses include source citations and confidence scores
   - Context is maintained across the conversation

3. **Reset Session**:
   - Click the refresh button to start a new chat session

## RAG Pipeline Details

### Document Processing
1. Documents are loaded using LangChain loaders
2. Text is split into chunks (1200 chars, 200 overlap)
3. Chunks are embedded using Azure OpenAI text-embedding-ada-002
4. Embeddings stored in FAISS vector store

### Query Processing
1. User question is embedded using Azure OpenAI
2. MMR retrieval finds relevant chunks (top 6, fetch_k=15)
3. GPT-4o generates grounded response with few-shot prompting
4. Guardrails check response validity
5. Sources and confidence returned

### Context Grounding
- All responses must be supported by retrieved documents
- Off-topic questions are politely rejected
- Hallucination detection prevents unsupported claims
- Source files are cited for transparency

## API Endpoints

### Backend (Port 8000)

- `GET /` - Health check
- `POST /upload` - Upload and process documents
- `POST /chat` - Chat with documents
- `POST /reset` - Reset chat session
- `GET /documents` - List uploaded documents
- `GET /health` - Check Azure OpenAI API key status

## Project Structure

```
.
├── backend/
│   ├── main.py              # FastAPI application
│   ├── rag_pipeline.py      # RAG implementation
│   └── requirements.txt     # Python dependencies
├── frontend/rag-app/
│   ├── src/
│   │   ├── app/
│   │   │   ├── components/
│   │   │   │   ├── file-upload/    # Upload component
│   │   │   │   └── chat/           # Chat component
│   │   │   └── services/
│   │   │       └── api.service.ts  # Backend API service
│   │   └── styles.scss      # Global styles
│   └── angular.json         # Angular configuration
├── data/
│   ├── uploads/             # Uploaded documents
│   └── vector_store/        # FAISS index
└── README.md
```

## Features in Detail

### Guardrails & Context Grounding
- Responses are generated ONLY from uploaded documents
- Questions outside document scope are rejected with helpful messages
- Each answer includes confidence score based on retrieval quality
- Source citations show which files were used for the answer

### Azure OpenAI Integration
- **GPT-4o**: Latest and most capable chat model for generating responses
- **text-embedding-ada-002**: High-quality embeddings for document vectorization
- **Few-shot prompting**: Enhanced responses with domain-specific examples

### Conversation Memory
- In-memory buffer stores chat history per session
- Context builds across messages
- Reset functionality for fresh starts

## Troubleshooting

### Azure OpenAI API Errors
- Ensure all required Azure OpenAI environment variables are set
- Verify your Azure OpenAI endpoint and API key are correct
- Check deployment names match your Azure OpenAI resource
- Use the `/health` endpoint to verify Azure OpenAI connection status

### Upload Errors
- Verify file format is supported
- Check file size (large files may take longer to process)
- Ensure backend is running on port 8000

### Chat Errors
- Upload at least one document before chatting
- Verify Azure OpenAI configuration is complete
- Check backend logs for detailed error messages