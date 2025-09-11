# Foundational - AI-Powered Document Chat Application

A full-stack application that enables users to upload PDF documents and chat with them using AI. The application consists of a React frontend and a FastAPI backend, providing an intuitive interface for document-based conversations.

## 🏗️ Architecture Overview

This project follows a modern full-stack architecture with clear separation of concerns:

```
Foundational/
├── frontend/          # React TypeScript application
├── backend/           # FastAPI Python application  
├── shared/            # Shared TypeScript schemas
└── dist/              # Built frontend assets
```

## 🚀 Tech Stacks

### Frontend (`/frontend`)
- **React 18** - Modern UI library with hooks
- **TypeScript** - Type-safe JavaScript
- **Vite** - Fast build tool and dev server
- **Tailwind CSS** - Utility-first CSS framework
- **Radix UI** - Accessible component primitives
- **React Query** - Data fetching and state management
- **Wouter** - Lightweight routing library
- **Framer Motion** - Animation library
- **Lucide React** - Icon library

### Backend (`/backend`)
- **FastAPI** - Modern Python web framework
- **LangChain** - Framework for LLM applications
- **OpenAI** - GPT models integration
- **PyPDF2** - PDF processing library
- **MongoDB** - Document database (via PyMongo)
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **Python-dotenv** - Environment variable management

### Shared (`/shared`)
- **Drizzle ORM** - Type-safe database ORM
- **PostgreSQL** - Primary database
- **Zod** - Schema validation

## 🔌 APIs Used

### External APIs
- **OpenAI GPT API** - For AI-powered chat responses
- **OpenAI Embeddings** - For document vectorization

### Internal APIs
The backend exposes a RESTful API with the following endpoints:

#### Health & Status
- `GET /` - Basic health check
- `GET /health` - Detailed health status

#### Document Management
- `POST /upload` - Upload and process PDF files
- `GET /files` - Retrieve all uploaded files
- `DELETE /files/{file_id}` - Delete specific files

#### Chat & Sessions
- `POST /session` - Create new chat session
- `GET /sessions` - Get all active sessions
- `DELETE /session/{session_id}` - Delete specific session
- `POST /chat/{session_id}` - Send message to document
- `GET /messages/{session_id}` - Get chat history

## 🛠️ How to Use the Whole Project

### Prerequisites

Before running the application, ensure you have:

- **Node.js** (version 16 or higher)
- **Python** (version 3.8 or higher)
- **OpenAI API Key** - Get one from [OpenAI Platform](https://platform.openai.com/)
- **MongoDB** - Running instance (local or cloud)
- **PostgreSQL** - Database instance

### 1. Clone the Repository

```bash
git clone <repository-url>
cd peergenaicertifications/Foundational
```

### 2. Backend Setup

Navigate to the backend directory and set up the Python environment:

```bash
cd backend

# Create and activate virtual environment
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True

# Model Configuration
DEFAULT_MODEL=gpt-3.5-turbo
MAX_TOKENS=1000
TEMPERATURE=0.7

# File Configuration
MAX_FILE_SIZE=10485760  # 10MB in bytes

# Database Configuration
MONGODB_URI=mongodb://localhost:27017/chatpdf
```

#### Start the Backend Server

```bash
# Development mode with auto-reload
python src/main.py

# Or using uvicorn directly
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at `http://localhost:8000`

### 3. Frontend Setup

Open a new terminal and navigate to the frontend directory:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Access the Application

1. Open your browser and go to `http://localhost:3000`
2. Upload a PDF document using the file upload interface
3. Start chatting with your document using the chat interface
4. Create multiple sessions for different documents
5. View chat history and manage sessions

## 📱 Features

### Document Management
- **PDF Upload** - Upload PDF documents up to 10MB
- **Text Extraction** - Automatic text extraction from PDFs
- **Vector Storage** - Documents are vectorized for semantic search
- **File Management** - View and delete uploaded files

### Chat Interface
- **AI-Powered Chat** - Chat with documents using OpenAI GPT
- **Session Management** - Multiple concurrent chat sessions
- **Message History** - Persistent chat history per session
- **Context Awareness** - AI responses based on document content

### User Experience
- **Responsive Design** - Works on desktop and mobile devices
- **Dark/Light Theme** - Theme switching capability
- **Real-time Updates** - Live chat interface
- **Error Handling** - Comprehensive error management
- **Loading States** - Visual feedback during operations

## 🔧 Development

### Project Structure

```
Foundational/
├── frontend/
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   │   ├── chat/       # Chat-related components
│   │   │   ├── sidebar/    # Sidebar components
│   │   │   └── ui/         # Base UI components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── lib/            # Utility libraries
│   │   ├── pages/          # Page components
│   │   └── App.tsx         # Main application
│   ├── package.json        # Dependencies and scripts
│   └── vite.config.ts      # Vite configuration
├── backend/
│   ├── src/
│   │   ├── config/         # Configuration files
│   │   ├── services/       # Business logic services
│   │   ├── utils/          # Utility functions
│   │   └── main.py         # FastAPI application
│   ├── requirements.txt    # Python dependencies
│   └── README.md          # Backend documentation
└── shared/
    └── schema.ts          # Shared TypeScript schemas
```

### Available Scripts

#### Frontend Scripts
```bash
npm run dev      # Start development server
npm run build    # Build for production
npm run start    # Preview production build
```

#### Backend Scripts
```bash
python src/main.py                    # Start development server
uvicorn src.main:app --reload         # Start with uvicorn
```

### API Documentation

Once the backend is running, you can access:
- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## 🚀 Production Deployment

### Frontend Deployment
1. Build the application: `npm run build`
2. Deploy the `dist/public` directory to your hosting service
3. Configure your web server to serve the built files

### Backend Deployment
1. Set `DEBUG=False` in environment variables
2. Use a production ASGI server like Gunicorn
3. Configure proper CORS origins
4. Set up reverse proxy (nginx)
5. Configure logging and monitoring

## 🐛 Troubleshooting

### Common Issues

1. **Backend not starting**:
   - Check if OpenAI API key is set correctly
   - Ensure MongoDB is running
   - Verify all dependencies are installed

2. **Frontend not connecting to backend**:
   - Ensure backend is running on port 8000
   - Check CORS configuration
   - Verify API proxy settings in vite.config.ts

3. **File upload issues**:
   - Check file size limits
   - Ensure file is a valid PDF
   - Verify backend file processing service

4. **Chat not working**:
   - Verify OpenAI API key is valid
   - Check if document was processed successfully
   - Ensure session ID is correct

### Debug Mode

Enable debug mode by setting `DEBUG=True` in the backend `.env` file for detailed error messages and logging.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 📞 Support

For support and questions:
- Check the troubleshooting section
- Review the API documentation
- Open an issue in the repository

---

**Note**: This application requires an OpenAI API key to function. Make sure to keep your API key secure and never commit it to version control.
