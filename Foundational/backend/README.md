# ChatPDF FastAPI Server

A FastAPI-based server for PDF document chat using LangChain and OpenAI.

## Features

- Upload and process PDF documents
- Chat with documents using LangChain and OpenAI
- Session management for multiple conversations
- RESTful API with automatic documentation
- CORS support for frontend integration

## Setup

### 1. Create and Activate Virtual Environment

```bash
# Navigate to the server directory
cd server

# Activate the virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Edit the `.env` file and add your OpenAI API key:

```bash
# Copy the example and add your API key
cp .env.example .env

# Edit .env file
nano .env
```

Set your OpenAI API key:
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 4. Run the Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

## API Documentation

Once the server is running, you can access:

- **Interactive API docs**: `http://localhost:8000/docs`
- **ReDoc documentation**: `http://localhost:8000/redoc`

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check

### Document Management
- `POST /upload` - Upload a PDF file
- `GET /sessions` - Get all active chat sessions
- `DELETE /sessions/{session_id}` - Delete a specific session

### Chat
- `POST /chat` - Chat with an uploaded document

## Usage Examples

### Upload a PDF
```bash
curl -X POST "http://localhost:8000/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"
```

### Chat with Document
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is this document about?",
    "session_id": "your-session-id"
  }'
```

## Configuration

The following environment variables can be configured in `.env`:

- `OPENAI_API_KEY` - Your OpenAI API key (required)
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)
- `DEBUG` - Debug mode (default: True)
- `DEFAULT_MODEL` - OpenAI model (default: gpt-3.5-turbo)
- `MAX_TOKENS` - Maximum tokens for responses (default: 1000)
- `TEMPERATURE` - Model temperature (default: 0.7)
- `MAX_FILE_SIZE` - Maximum file size in bytes (default: 10MB)

## Project Structure

```
server/
├── venv/                 # Virtual environment
├── main.py              # FastAPI application
├── langchain_service.py # LangChain integration
├── requirements.txt     # Python dependencies
├── .env                # Environment variables
└── README.md           # This file
```

## Dependencies

- **FastAPI**: Modern, fast web framework
- **LangChain**: Framework for LLM applications
- **OpenAI**: GPT models integration
- **FAISS**: Vector similarity search
- **PyPDF2**: PDF processing
- **Uvicorn**: ASGI server

## Development

### Adding New Features

1. Create new endpoints in `main.py`
2. Add corresponding methods in `langchain_service.py`
3. Update this README with new API documentation

### Error Handling

The API includes comprehensive error handling:
- File validation (type, size)
- Session management
- OpenAI API errors
- General exception handling

## Production Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper CORS origins
3. Use a production ASGI server like Gunicorn
4. Set up proper logging
5. Configure reverse proxy (nginx)

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**: Make sure your API key is set in `.env`
2. **File Upload Issues**: Check file size and format restrictions
3. **Memory Issues**: Large PDFs may require more memory
4. **Session Not Found**: Ensure you're using the correct session_id

### Logs

Check the console output for detailed error messages and debugging information.
