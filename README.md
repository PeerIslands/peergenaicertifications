# RAG Document Chat Application

A powerful Retrieval-Augmented Generation (RAG) application built with Streamlit that allows users to upload documents, store them as vectors in MongoDB, and chat with an AI assistant that can answer questions based on the document content.

## Features

🔹 **Document Upload**: Support for PDF, DOCX, and TXT files  
🔹 **Vector Storage**: Documents are chunked and stored as embeddings in MongoDB  
🔹 **Smart Search**: Uses sentence transformers for semantic similarity search  
🔹 **AI Chat**: Powered by OpenAI's GPT models for intelligent responses  
🔹 **Modern UI**: Beautiful Streamlit interface with custom styling  
🔹 **Document Management**: View, delete, and manage uploaded documents  
🔹 **Source Attribution**: Shows which document chunks were used for each answer  

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
   cd Basic\ RAG
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
   ```

## Usage

1. **Start the application**
   ```bash
   streamlit run main.py
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
Basic RAG/
├── main.py                 # Main Streamlit application
├── config.py              # Configuration settings
├── document_processor.py   # Document processing and embedding
├── mongodb_client.py       # MongoDB operations
├── rag_chatbot.py         # RAG chatbot logic
├── requirements.txt       # Python dependencies
├── sample_env.txt         # Sample environment variables
├── test_setup.py         # Setup verification script
├── start_app.sh          # Startup script
└── README.md             # This file
```

## Configuration

The application can be configured through environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | OpenAI API key (required) | - |
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/` |
| `MONGODB_DB_NAME` | Database name | `rag_database` |
| `MONGODB_COLLECTION_NAME` | Collection name | `documents` |

## Technical Details

### Document Processing
- **Text Extraction**: Uses PyPDF2 for PDFs, python-docx for DOCX files
- **Chunking**: Splits documents into 1000-character chunks with 200-character overlap
- **Embeddings**: Uses `all-MiniLM-L6-v2` sentence transformer model

### Vector Search
- **Storage**: Embeddings stored in MongoDB with document metadata
- **Similarity**: Cosine similarity for finding relevant chunks
- **Retrieval**: Top-k retrieval (default: 5 chunks)

### AI Integration
- **Model**: OpenAI GPT-3.5-turbo
- **Context**: Relevant chunks provided as context to the LLM
- **Temperature**: 0.7 for balanced creativity and accuracy

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**
   - Ensure MongoDB is running
   - Check connection string format
   - Verify network connectivity

2. **OpenAI API Errors**
   - Verify API key is set correctly
   - Check API quota and billing
   - Ensure stable internet connection

3. **Document Processing Errors**
   - Check file format is supported
   - Verify file is not corrupted
   - Ensure sufficient disk space

### Error Messages

- **"OpenAI API Key is not set"**: Set the `OPENAI_API_KEY` environment variable
- **"MongoDB connection failed"**: Check MongoDB service and connection string
- **"No documents uploaded yet"**: Upload documents before chatting

## Extending the Application

### Adding New File Types
1. Add extraction method to `DocumentProcessor`
2. Update file type validation in Streamlit interface
3. Test with sample files

### Custom Embedding Models
1. Update `EMBEDDING_MODEL` in `config.py`
2. Ensure model compatibility with sentence-transformers
3. Consider re-processing existing documents

### Advanced Vector Search
- Implement MongoDB Atlas Vector Search
- Add metadata filtering
- Implement hybrid search (keyword + semantic)

## Performance Considerations

- **Chunk Size**: Balance between context and precision
- **Embedding Model**: Larger models = better quality, slower processing
- **MongoDB Indexing**: Create appropriate indexes for better query performance
- **Caching**: Consider caching embeddings for frequently accessed documents

## Security Notes

- Store API keys securely (environment variables, not in code)
- Validate uploaded files before processing
- Implement rate limiting for production use
- Consider data privacy implications for sensitive documents

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).

## Support

For questions or issues:
1. Check the troubleshooting section
2. Review error messages in the application
3. Create an issue in the repository
