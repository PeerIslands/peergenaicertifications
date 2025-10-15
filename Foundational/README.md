# PI PDF RAG - Foundational

A powerful Retrieval-Augmented Generation (RAG) system for processing and querying PDF documents using modern AI technologies with MongoDB vector storage.

## 🚀 Features

- **PDF Document Processing**: Upload and extract text from PDF documents with real-time status updates
- **Advanced Text Chunking**: Intelligent document segmentation using LangChain's RecursiveCharacterTextSplitter
- **Vector Search**: Semantic similarity search with OpenAI embeddings stored in MongoDB
- **Hybrid Search**: Combines vector search and text search for better results
- **AI-Powered Q&A**: Generate intelligent responses based on document content with source attribution
- **Modern Web Interface**: React-based UI with Tailwind CSS and shadcn/ui components
- **Document Management**: View, delete, and manage uploaded documents
- **Real-time Updates**: Automatic UI updates during document processing
- **Source Viewing**: View full source content with detailed metadata

## 🆕 MongoDB Vector Store Integration

This project uses **MongoDB** as a vector store for enhanced RAG capabilities:

- **Persistent Storage**: Documents and embeddings stored in MongoDB
- **Vector Search**: MongoDB Atlas vector search for semantic similarity
- **Hybrid Search**: Combines vector and text search for optimal results
- **Document Management**: Full CRUD operations for documents and chunks
- **Performance Optimized**: Indexed queries and connection pooling
- **Scalable**: Supports large document collections

📖 **See [MONGODB_SETUP.md](./MONGODB_SETUP.md) for detailed MongoDB setup.**

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS + shadcn/ui
- **Backend**: Node.js + Express + TypeScript
- **AI**: OpenAI GPT models + OpenAI Embeddings
- **Database**: MongoDB with vector search
- **Vector Search**: MongoDB Atlas Vector Search + LangChain
- **PDF Processing**: pdf-parse
- **Build Tools**: Vite + esbuild
- **State Management**: TanStack Query (React Query)
- **Routing**: Wouter

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- MongoDB Atlas account (or local MongoDB installation)
- OpenAI API key

### Installation
```bash
# Install dependencies
npm install

# Set environment variables
export OPENAI_API_KEY="your_openai_api_key_here"
export MONGODB_URI="your_mongodb_connection_string"
export MONGODB_DATABASE="pdf_rag"

# Start development server
npm run dev
```

### Environment Variables
```bash
OPENAI_API_KEY=your_openai_api_key_here
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=pdf_rag
PORT=8080
```

## 📚 API Endpoints

### Document Management
- `GET /api/documents` - List all processed documents
- `POST /api/documents/upload` - Upload and process PDF documents
- `GET /api/documents/:id` - Get specific document details
- `DELETE /api/documents/:id` - Delete document and all associated chunks

### Search & Analytics
- `POST /api/search` - Perform RAG search queries
- `GET /api/stats` - Get processing statistics and document counts

### Features
- **Real-time Processing**: Asynchronous PDF processing with status updates
- **Hybrid Search**: Combines vector and text search for optimal results
- **Source Attribution**: Detailed source information with relevance scores
- **Document Management**: Full CRUD operations with safety checks

## 🎨 User Interface Features

- **Modern Design**: Clean, responsive UI built with Tailwind CSS and shadcn/ui components
- **Document Upload**: Drag-and-drop PDF upload with file validation and progress tracking
- **Real-time Status**: Live updates showing document processing status (uploading, processing, ready, error)
- **Interactive Search**: Search interface with loading states and error handling
- **Source Viewing**: Click to view full source content in a modal dialog
- **Document Management**: Delete documents with confirmation dialogs and safety checks
- **Responsive Layout**: Works on desktop and mobile devices
- **Toast Notifications**: User feedback for all actions (success, error, info)
- **Processing Stats**: Real-time statistics showing document counts and storage usage

## 🧪 Testing

Test the application:
```bash
# Set your API keys
export OPENAI_API_KEY="your_key_here"
export MONGODB_URI="your_mongodb_connection_string"

# Start the application
npm run dev

# The application will be available at http://localhost:8080
```

## 📖 Documentation

- [MongoDB Setup Guide](./MONGODB_SETUP.md) - MongoDB configuration and vector search setup
- [API Documentation](./server/routes.ts) - Backend API endpoints
- [Frontend Components](./client/src/components/) - React component library
- [LangChain Integration](./LANGCHAIN_README.md) - LangChain usage details

## 🔧 Development

```bash
# Development mode
npm run dev

# Build for production
npm run build

# Start production server
npm start

# Type checking
npm run check
```

## 🎯 Use Cases

- **Document Q&A**: Ask questions about uploaded PDFs with source attribution
- **Research Assistant**: Extract insights from research papers with full source viewing
- **Knowledge Base**: Build searchable document repositories with real-time updates
- **Content Analysis**: Analyze and summarize document content with relevance scoring
- **Document Management**: Upload, view, and delete documents with processing status tracking
- **Legal Document Review**: Search through legal documents efficiently with detailed source information

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using MongoDB, LangChain, React, and modern web technologies**