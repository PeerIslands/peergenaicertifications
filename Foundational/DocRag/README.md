# RAG PDF Query System

A complete Retrieval-Augmented Generation (RAG) system for querying PDF documents using LangChain, FAISS, Azure OpenAI, FastAPI, and React.

## 🌟 Features

- **PDF Ingestion**: Upload and process multiple PDF documents
- **Vector Search**: FAISS-based similarity search for efficient retrieval
- **Azure OpenAI Integration**: Powered by Azure's GPT models
- **Modern UI**: Beautiful React frontend with real-time status updates
- **RESTful API**: FastAPI backend with comprehensive endpoints
- **Source Attribution**: Track which documents were used to generate answers

## 🏗️ Architecture

```
DocRag/
├── backend/              # FastAPI backend
│   ├── main.py          # API endpoints
│   ├── rag_service.py   # RAG logic with LangChain
│   ├── requirements.txt # Python dependencies
│   ├── .env.example     # Environment template
│   └── pdfs/           # PDF storage directory
│
└── frontend/            # React frontend
    ├── src/
    │   ├── App.jsx     # Main application
    │   ├── App.css     # Styles
    │   └── main.jsx    # Entry point
    ├── package.json    # Node dependencies
    └── vite.config.js  # Vite configuration
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Azure OpenAI account with API access

### Backend Setup

1. **Navigate to backend directory:**
```bash
cd backend
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables:**
```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:
```env
AZURE_OPENAI_API_KEY=your_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=gpt-4
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=text-embedding-ada-002
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

5. **Run the backend:**
```bash
python main.py
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory:**
```bash
cd frontend
```

2. **Install dependencies:**
```bash
npm install
```

3. **Run the development server:**
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📁 Adding PDF Files

You can add PDF files in two ways:

1. **Upload via UI**: Use the web interface to upload PDFs
2. **Manual placement**: Place PDFs directly in `backend/pdfs/` directory

## 🔌 API Endpoints

### `GET /`
Health check endpoint

### `POST /api/ingest`
Upload and ingest PDF files
- **Request**: `multipart/form-data` with PDF files
- **Response**: `{"message": "...", "files_processed": 2}`

### `POST /api/query`
Query the ingested documents
- **Request**: `{"query": "your question", "top_k": 3}`
- **Response**: `{"answer": "...", "sources": [...]}`

### `GET /api/status`
Get system status
- **Response**: `{"initialized": true, "documents_count": 42}`

### `DELETE /api/reset`
Reset the system and clear all documents

## 🛠️ Technology Stack

### Backend
- **FastAPI**: Modern, fast web framework
- **LangChain**: RAG orchestration framework
- **FAISS**: Facebook AI Similarity Search (vector store)
- **Azure OpenAI**: GPT-4 and embedding models
- **PyPDF**: PDF parsing library

### Frontend
- **React 18**: UI library
- **Vite**: Next-generation frontend tooling
- **Axios**: HTTP client
- **Modern CSS**: Gradients, animations, responsive design

## 💡 Usage Example

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in your browser
3. Upload one or more PDF files
4. Wait for ingestion to complete
5. Ask questions using the query interface or sample questions
6. View AI-generated answers with source references

## 🎨 Sample Questions

The UI provides sample questions like:
- "What is the main topic of the document?"
- "Can you summarize the key points?"
- "What are the important findings?"
- "Tell me about the methodology used"

## 📝 Environment Variables

Create a `.env` file in the `backend` directory with:

```env
AZURE_OPENAI_API_KEY=your_azure_openai_api_key
AZURE_OPENAI_ENDPOINT=https://your-resource-name.openai.azure.com/
AZURE_OPENAI_CHAT_DEPLOYMENT=your_chat_deployment_name
AZURE_OPENAI_EMBEDDING_DEPLOYMENT=your_embedding_deployment_name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

## 🐛 Troubleshooting

### Backend Issues
- Ensure all Python dependencies are installed
- Verify Azure OpenAI credentials in `.env`
- Check that port 8000 is available

### Frontend Issues
- Ensure Node.js dependencies are installed (`npm install`)
- Verify backend is running at `http://localhost:8000`
- Check that port 3000 is available

### FAISS Issues
- If you encounter FAISS installation issues, ensure you have the correct version for your OS
- On some systems, you may need `faiss-gpu` instead of `faiss-cpu`

## 🔒 Security Notes

- Never commit `.env` files to version control
- Keep your Azure OpenAI API keys secure
- The `.gitignore` files are configured to exclude sensitive files

## 📄 License

This project is open source and available for educational purposes.

## 🤝 Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## 📚 Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [FAISS Documentation](https://faiss.ai/)
- [Azure OpenAI Service](https://azure.microsoft.com/en-us/products/ai-services/openai-service)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

