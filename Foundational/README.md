# PI PDF RAG - Foundational

A powerful Retrieval-Augmented Generation (RAG) system for processing and querying PDF documents using modern AI technologies.

## 🚀 Features

- **PDF Document Processing**: Upload and extract text from PDF documents
- **Advanced Text Chunking**: Intelligent document segmentation using LangChain
- **Vector Search**: Semantic similarity search with OpenAI embeddings
- **AI-Powered Q&A**: Generate intelligent responses based on document content
- **Modern Web Interface**: React-based UI with Tailwind CSS
- **Real-time Processing**: WebSocket support for live updates

## 🆕 New: LangChain Integration

This project now includes **LangChain** integration for enhanced RAG capabilities:

- **Advanced Text Splitting**: Recursive character-based splitting with semantic coherence
- **Vector Store**: In-memory vector store for efficient similarity search
- **Runnable Chains**: Structured LLM workflows with proper input/output handling
- **Enhanced Prompts**: Structured prompt templates for consistent responses
- **Performance Metrics**: Search time tracking and relevance scoring

📖 **See [LANGCHAIN_README.md](./LANGCHAIN_README.md) for detailed LangChain usage.**

## 🛠️ Tech Stack

- **Frontend**: React 18 + TypeScript + Tailwind CSS
- **Backend**: Node.js + Express + TypeScript
- **AI**: OpenAI GPT models via OpenRouter
- **Database**: Drizzle ORM with PostgreSQL
- **Vector Search**: LangChain + OpenAI Embeddings
- **PDF Processing**: pdf-parse
- **Build Tools**: Vite + esbuild

## 🚀 Quick Start

### Prerequisites
- Node.js 18+
- PostgreSQL database
- OpenRouter API key

### Installation
```bash
# Install dependencies
npm install

# Set environment variables
export OPENROUTER_API_KEY="your_openrouter_api_key_here"

# Start development server
npm run dev
```

### Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
DATABASE_URL=your_postgresql_connection_string
```

## 📚 API Endpoints

### Core RAG Endpoints
- `POST /api/documents` - Upload and process PDF documents
- `POST /api/search` - Perform RAG search queries
- `GET /api/documents` - List all processed documents

### Enhanced LangChain Features
- **Integrated Text Splitting**: Advanced document chunking in RAG service
- **Enhanced Prompts**: Structured prompt templates in OpenAI service
- **LLM Workflows**: RunnableSequence chains for better response generation

## 🧪 Testing

Test the LangChain integration:
```bash
# Set your API key
export OPENROUTER_API_KEY="your_key_here"

# Run LangChain tests
node test-langchain.mjs
```

## 📖 Documentation

- [LangChain Integration Guide](./LANGCHAIN_README.md) - Comprehensive LangChain usage
- [API Documentation](./server/routes.ts) - Backend API endpoints
- [Frontend Components](./client/src/components/) - React component library

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

# Database migrations
npm run db:push
```

## 🎯 Use Cases

- **Document Q&A**: Ask questions about uploaded PDFs
- **Research Assistant**: Extract insights from research papers
- **Knowledge Base**: Build searchable document repositories
- **Content Analysis**: Analyze and summarize document content
- **Legal Document Review**: Search through legal documents efficiently

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details

---

**Built with ❤️ using LangChain, React, and modern web technologies**