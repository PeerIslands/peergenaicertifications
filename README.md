# RAG Chat App with Pre-loaded PDF Documents

A complete local Retrieval-Augmented Generation (RAG) chat application that automatically processes PDF documents from the files directory and allows querying them in natural language.

## 🏗️ Architecture

- **Frontend**: React + TailwindCSS
- **Backend**: FastAPI (Python)
- **Database**: MongoDB with vector indexing
- **Model**: Local LLaMA 3 (via Ollama)
- **Embeddings**: HuggingFace sentence-transformers/all-MiniLM-L6-v2

## 📁 Project Structure

```
rag-chat-app/
├── backend-rag-chat/             # FastAPI Backend
│   ├── main.py                   # FastAPI application
│   ├── config.py                 # Configuration settings
│   ├── routes/                   # API routes
│   │   ├── documents.py          # Document management endpoints
│   │   └── chat.py               # Chat endpoints
│   ├── services/                 # Business logic
│   │   ├── file_processor.py     # File processing from directory
│   │   ├── embeddings.py         # Text embeddings
│   │   ├── vector_store.py       # MongoDB vector operations
│   │   └── rag_pipeline.py       # RAG pipeline
│   ├── models/                   # Pydantic models
│   │   ├── chat_request.py       # Chat request/response models
│   │   └── pdf_metadata.py       # PDF metadata models
│   ├── requirements.txt          # Python dependencies
│   └── env.example               # Environment template
├── frontend-rag-chat/            # React Frontend
│   ├── src/                      # React source code
│   │   ├── components/           # React components
│   │   │   ├── ChatWindow.jsx   # Chat display component
│   │   │   └── ChatInput.jsx    # Chat input component
│   │   ├── services/            # API services
│   │   │   └── api.js           # Axios API client
│   │   ├── App.js               # Main React app
│   │   └── index.js             # React entry point
│   ├── public/                   # Static files
│   ├── package.json             # Node.js dependencies
│   └── tailwind.config.js        # TailwindCSS config
├── run_backend.sh               # Backend startup script
├── run_frontend.sh              # Frontend startup script
├── setup.sh                     # Automated setup script
├── docker-compose.yml           # Docker setup
└── README.md                    # This file
```

## 🚀 Setup Instructions

### Prerequisites

1. **Python 3.8+**
2. **Node.js 16+**
3. **MongoDB** (local installation or MongoDB Atlas)
4. **Ollama** with LLaMA 3 model

### 1. Install Ollama and LLaMA 3

```bash
# Install Ollama (macOS)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull LLaMA 3 model
ollama pull llama3
```

### 2. Setup Backend

```bash
# Navigate to backend directory
cd backend-rag-chat

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp env.example .env
# Edit .env with your MongoDB URI and other settings

# Start MongoDB (if running locally)
mongod

# Run the backend
uvicorn main:app --reload
```

### 3. Setup Frontend

```bash
# Navigate to frontend directory
cd frontend-rag-chat

# Install dependencies
npm install

# Start the frontend
npm start
```

### 4. Access the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=rag_chat_db
EMBEDDING_MODEL_NAME=sentence-transformers/all-MiniLM-L6-v2
LLAMA_MODEL_ENDPOINT=http://localhost:11434/api/generate
MAX_FILES=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
TOP_K_CHUNKS=5
```

### MongoDB Vector Index

The application will automatically create a vector index for similarity search. For production, consider using MongoDB Atlas with vector search capabilities.

## 📖 Usage

1. **Automatic Processing**: PDF files in the `files/` directory are automatically processed on startup
2. **Chat**: Ask questions about the loaded documents
3. **View Sources**: See which documents were used to answer your questions
4. **Conversation Memory**: The system maintains context across multiple questions in a session

## 🔌 API Endpoints

### Document Management
- `POST /api/reload` - Reload and process all files from files directory
- `GET /api/status` - Get current document status

### Chat
- `POST /api/chat` - Send chat message
- `DELETE /api/reset` - Clear all documents
- `GET /api/health` - Health check

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Run development server
npm start

# Build for production
npm run build
```

## 🐳 Docker Support (Optional)

Create `Dockerfile` for backend:

```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Troubleshooting

### Common Issues

1. **MongoDB Connection**: Ensure MongoDB is running and accessible
2. **Ollama Connection**: Verify Ollama is running and LLaMA 3 model is available
3. **CORS Issues**: Check that frontend and backend are on correct ports
4. **Memory Issues**: Large PDFs may require more RAM for processing

### Logs

- Backend logs: Check terminal where uvicorn is running
- Frontend logs: Check browser console
- MongoDB logs: Check MongoDB log files

## 📝 Features

- ✅ Automatic PDF processing from files directory
- ✅ Text extraction and chunking
- ✅ Vector embeddings with HuggingFace
- ✅ MongoDB vector storage
- ✅ RAG pipeline with LLaMA 3
- ✅ Real-time chat interface
- ✅ Source attribution
- ✅ Conversation memory and context
- ✅ Responsive design
- ✅ Error handling