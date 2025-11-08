# RAG Document Chat Application

A production-ready Retrieval-Augmented Generation (RAG) application built with Streamlit that allows users to upload documents, store them as vectors in MongoDB, and chat with an AI assistant that can answer questions based on the document content.

## Features

🔹 **Document Upload**: Support for PDF, DOCX, and TXT files  
🔹 **Vector Storage**: Documents are chunked and stored as embeddings in MongoDB  
🔹 **Smart Search**: Uses sentence transformers for semantic similarity search  
🔹 **AI Chat**: Powered by OpenAI's GPT models for intelligent responses  
🔹 **Modern UI**: Beautiful Streamlit interface with custom styling  
🔹 **Document Management**: View, delete, and manage uploaded documents  
🔹 **Source Attribution**: Shows which document chunks were used for each answer  
🔹 **Connection Pooling**: Efficient MongoDB connection management  
🔹 **Comprehensive Logging**: Full application logging for debugging and monitoring  
🔹 **Error Handling**: Robust validation and error handling throughout  
🔹 **Code Quality**: Linting, formatting, and comprehensive test coverage  

## Architecture

```
User Upload → Document Processing → Text Chunking → Embeddings → MongoDB Storage
                                                                        ↓
User Query → Query Embedding → Similarity Search → Context Retrieval → LLM Response
```

## Prerequisites

- Python 3.8+
- MongoDB (local or cloud)
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd peergenaicertifications
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up MongoDB**
   - **Local MongoDB**: Install and start MongoDB service
     ```bash
     # macOS with Homebrew
     brew install mongodb-community
     brew services start mongodb-community
     
     # Or run manually
     mongod --dbpath /path/to/your/db
     ```
   - **MongoDB Atlas**: Get connection string from MongoDB Atlas

4. **Configure environment variables**
   
   **Option A: Using .env file (Recommended)**
   ```bash
   # Copy the sample environment file
   cp sample_env.txt .env
   
   # Edit .env file with your actual values
   # Replace 'your_openai_api_key_here' with your actual OpenAI API key
   ```
   
   **Option B: Using shell environment variables**
   ```bash
   # Set your OpenAI API key
   export OPENAI_API_KEY="your-openai-api-key-here"
   
   # Optional: Set custom MongoDB URI (default: mongodb://localhost:27017/)
   export MONGODB_URI="your-mongodb-connection-string"
   
   # Optional: Set custom database name (default: rag_database)
   export MONGODB_DB_NAME="your-database-name"
   
   # Optional: Set logging level (default: INFO)
   export LOG_LEVEL="INFO"
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run main.py
   ```
   
   Or use the provided startup script:
   ```bash
   ./start_app.sh
   ```

2. **Upload Documents**
   - Use the file uploader in the left column
   - Select PDF, DOCX, or TXT files
   - Click "Process Documents" to upload and vectorize

3. **Chat with Documents**
   - Ask questions in the chat interface
   - The AI will search through your documents and provide answers
   - View source documents used for each response

## Project Structure

```
peergenaicertifications/
├── main.py                    # Main Streamlit application
├── config.py                  # Configuration settings and logging setup
├── document_processor.py      # Document processing and embedding
├── mongodb_client.py          # MongoDB operations with connection pooling
├── rag_chatbot.py            # RAG chatbot logic
├── requirements.txt          # Python dependencies
├── sample_env.txt            # Sample environment variables
├── test_setup.py            # Setup verification script
├── start_app.sh             # Startup script
├── check.sh                 # Run all quality checks
├── run_tests.sh             # Run test suite
├── run_linters.sh           # Run code linters
├── conftest.py              # Pytest configuration and fixtures
├── pytest.ini               # Pytest settings
├── .pylintrc                # Pylint configuration
├── .flake8                  # Flake8 configuration
├── .coveragerc              # Coverage configuration
├── .gitignore               # Git ignore patterns
├── tests/                   # Test suite
│   ├── __init__.py
│   ├── test_config.py
│   ├── test_mongodb_client.py
│   ├── test_document_processor.py
│   └── test_rag_chatbot.py
└── README.md                # This file
```

## Development

### Running Tests

Run the entire test suite with coverage:
```bash
./run_tests.sh
```

Or run tests directly with pytest:
```bash
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing
```

View coverage report:
```bash
open htmlcov/index.html
```

### Code Quality Checks

Run all quality checks (formatting, linting, tests):
```bash
./check.sh
```

This single command will:
- ✅ Check code formatting with Black
- ✅ Run Flake8 linter
- ✅ Run Pylint analysis
- ✅ Execute test suite with coverage

Individual checks:
```bash
# Run linters only
./run_linters.sh

# Format code
black . --exclude venv

# Run flake8
flake8 . --exclude=venv,tests

# Run pylint
pylint *.py --rcfile=.pylintrc
```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `MONGODB_DB_NAME` | Database name | `rag_database` |
| `MONGODB_COLLECTION_NAME` | Collection name | `documents` |
| `MONGODB_POOL_SIZE` | Minimum connection pool size | `10` |
| `MONGODB_MAX_POOL_SIZE` | Maximum connection pool size | `50` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) | `INFO` |
| `LOG_FILE` | Log file path | `app.log` |
| `EMBEDDING_MODEL` | Sentence transformer model | `all-MiniLM-L6-v2` |
| `CHUNK_SIZE` | Document chunk size in characters | `1000` |
| `CHUNK_OVERLAP` | Chunk overlap in characters | `200` |

## Technical Details

### Document Processing
- **Text Extraction**: Uses PyPDF2 for PDFs, python-docx for DOCX files
- **Chunking**: Splits documents into configurable chunks with overlap
- **Embeddings**: Uses sentence transformer models for vector generation
- **Validation**: Comprehensive input validation for all file types

### Vector Search
- **Storage**: Embeddings stored in MongoDB with document metadata
- **Similarity**: Cosine similarity for finding relevant chunks
- **Retrieval**: Top-k retrieval (default: 5 chunks)
- **Indexing**: Automatic index creation for optimized queries

### Database Connection
- **Connection Pooling**: Singleton pattern with configurable pool size
- **Resilience**: Automatic retry logic and error handling
- **Performance**: Reuses connections for better efficiency
- **Monitoring**: Connection state logging

### AI Integration
- **Model**: OpenAI GPT-3.5-turbo
- **Context**: Relevant chunks provided as context to the LLM
- **Temperature**: 0.7 for balanced creativity and accuracy
- **Error Handling**: Graceful handling of API errors and rate limits

### Logging
- **Framework**: Python logging module with file and console output
- **Levels**: Configurable logging levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Format**: Timestamp, module name, level, and message
- **Rotation**: Logs written to both file and stdout

### Error Handling
- **Validation**: Input validation at every layer
- **Exceptions**: Specific exception types for different error scenarios
- **User Feedback**: Clear error messages in the UI
- **Recovery**: Graceful degradation when services are unavailable

## Testing

### Test Coverage

The project includes comprehensive unit tests covering:
- Configuration management
- MongoDB operations and connection pooling
- Document processing and extraction
- RAG chatbot functionality
- Error handling and edge cases

### Running Specific Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_mongodb_client.py

# Run with verbose output
pytest -v

# Run with specific markers
pytest -m unit
```

### Test Structure

- **conftest.py**: Shared fixtures and mocks
- **test_config.py**: Configuration tests
- **test_mongodb_client.py**: Database operation tests
- **test_document_processor.py**: Document processing tests
- **test_rag_chatbot.py**: Chatbot functionality tests

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running: `brew services list | grep mongodb`
   - Check connection string format in `.env`
   - Verify network connectivity
   - Check logs in `app.log` for detailed error messages

2. **OpenAI API Errors**
   - Verify API key is set correctly: `echo $OPENAI_API_KEY`
   - Check API quota and billing at platform.openai.com
   - Ensure stable internet connection
   - Review error logs for specific API error codes

3. **Document Processing Errors**
   - Check file format is supported (PDF, DOCX, TXT)
   - Verify file is not corrupted
   - Ensure sufficient disk space
   - Check logs for validation errors

4. **Import Errors**
   - Ensure all dependencies are installed: `pip install -r requirements.txt`
   - Verify virtual environment is activated
   - Check Python version (3.8+)

### Error Messages

- **"OpenAI API Key is not set"**: Set the `OPENAI_API_KEY` environment variable
- **"MongoDB connection failed"**: Check MongoDB service and connection string
- **"No documents uploaded yet"**: Upload documents before chatting
- **"Query embedding cannot be empty"**: Ensure query text is provided
- **"Validation error"**: Check input format and requirements in logs

### Debugging

Enable debug logging for detailed information:
```bash
export LOG_LEVEL=DEBUG
streamlit run main.py
```

Check application logs:
```bash
tail -f app.log
```

## Extending the Application

### Adding New File Types
1. Add extraction method to `DocumentProcessor` class
2. Update file type validation in `_validate_file()` method
3. Add file extension to Streamlit uploader
4. Write unit tests for new file type
5. Update documentation

### Custom Embedding Models
1. Update `EMBEDDING_MODEL` in `config.py` or `.env`
2. Ensure model compatibility with sentence-transformers
3. Consider re-processing existing documents
4. Update tests with new model dimensions

### Advanced Vector Search
- Implement MongoDB Atlas Vector Search for better performance
- Add metadata filtering for targeted searches
- Implement hybrid search (keyword + semantic)
- Add query expansion and re-ranking

### Custom LLM Prompts
- Modify `system_prompt` in `rag_chatbot.py`
- Adjust temperature and token limits
- Implement conversation history
- Add custom response formatting

## Performance Considerations

### Optimization Tips
- **Chunk Size**: Balance between context quality and search precision
- **Embedding Model**: Larger models provide better quality but slower processing
- **Connection Pool**: Adjust pool size based on concurrent users
- **Caching**: Consider caching embeddings for frequently accessed documents
- **Batch Processing**: Process multiple documents in parallel
- **Index Optimization**: Ensure MongoDB indexes are properly configured

### Monitoring
- Monitor log file for errors and warnings
- Track response times in application logs
- Monitor MongoDB connection pool usage
- Track OpenAI API usage and costs

## Security Notes

- Store API keys securely (environment variables, not in code)
- Validate all uploaded files before processing
- Implement rate limiting for production use
- Consider data privacy implications for sensitive documents
- Use environment-specific configurations
- Regularly update dependencies for security patches
- Implement authentication for production deployments
- Use HTTPS for production deployments

## Best Practices

### Code Quality
- Run `./check.sh` before committing code
- Maintain test coverage above 80%
- Follow PEP 8 style guidelines
- Write descriptive docstrings
- Use type hints where applicable

### Development Workflow
1. Create feature branch
2. Write tests first (TDD)
3. Implement feature
4. Run quality checks: `./check.sh`
5. Commit with descriptive message
6. Create pull request

### Production Deployment
- Use environment-specific configuration files
- Enable production logging level (WARNING or ERROR)
- Set up log rotation
- Monitor application performance
- Implement health check endpoints
- Use process managers (PM2, Supervisor)
- Set up automated backups for MongoDB

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for new functionality
5. Run quality checks: `./check.sh`
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review logs in `app.log`
3. Review error messages in the application
4. Check existing issues in the repository
5. Create a new issue with detailed information

## Acknowledgments

Built with:
- [Streamlit](https://streamlit.io/) - Web framework
- [OpenAI](https://openai.com/) - Language models
- [MongoDB](https://www.mongodb.com/) - Vector database
- [Sentence Transformers](https://www.sbert.net/) - Embedding models
- [pytest](https://pytest.org/) - Testing framework
