# Document RAG Chat Application

A Streamlit application that allows you to upload documents (PDF, DOCX, TXT) and chat with them using LangChain and MongoDB Atlas as the vector store.

## Features

- 📄 Upload multiple document files (PDF, DOCX, TXT)
- 💬 Chat interface to ask questions about the uploaded documents
- 🔍 Retrieval-Augmented Generation (RAG) using LangChain
- 🗄️ Persistent vector store using MongoDB Atlas
- 📚 Source document citations
- 📝 Comprehensive logging for debugging and monitoring
- ⚙️ Customizable database, collection, and index names

## Installation

1. Clone this repository
2. Install the required packages:

```bash
pip install -r requirements.txt
```

Note: The requirements include test dependencies (pytest, pytest-mock). If you only want to run the application without testing, you can install without test dependencies, but the full requirements.txt is recommended.

## Usage

1. Run the Streamlit app:

```bash
streamlit run app.py
```

2. In the left column:
   - Enter your OpenAI API key
   - Enter your MongoDB Atlas connection string
   - Configure database, collection, and index names (optional, defaults: `document_rag`, `documents`, `vector_index`)
   - Upload one or more document files (PDF, DOCX, or TXT)
   - Click "Process Documents"

3. Start chatting in the main interface!

## MongoDB Atlas Setup

1. Create a MongoDB Atlas account at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create a new cluster (free tier available)
3. Get your connection string from the Atlas dashboard
4. Create a vector search index in your database:
   - Go to Atlas Search
   - Create a vector search index on your collection
   - Use the default configuration (1536 dimensions for OpenAI embeddings)
   - Name it (default: "vector_index")

## Configuration

- The app uses OpenAI's GPT-3.5-turbo model by default
- You can modify the model and other settings in `app.py`
- Vector store uses MongoDB Atlas for persistent storage
- You'll need a MongoDB Atlas account and connection string
- Create a vector search index in MongoDB Atlas before using the app
- **Default database name**: `document_rag` (customizable in UI)
- **Default collection name**: `documents` (customizable in UI)
- **Default index name**: `vector_index` (customizable in UI)

### Custom Database Configuration

You can customize the database, collection, and index names in the Streamlit UI. The values you enter will be used instead of the defaults. If you leave a field empty, the default value will be used.

## Supported Document Formats

The application supports the following document formats:
- **PDF** (.pdf) - Using PyPDFLoader
- **DOCX** (.docx) - Using Docx2txtLoader
- **TXT** (.txt) - Using TextLoader

You can upload multiple files of different formats in a single session.

## Logging

The application includes comprehensive logging that tracks:
- Document loading and processing steps (all supported formats)
- Document chunking and vector store creation
- Chat query processing and document retrieval
- Response generation timing and statistics

Logs are written to:
- Console output (INFO level and above)
- `document_rag.log` file (all log levels)

To adjust logging verbosity, modify the `logging.basicConfig` level in `app.py` (DEBUG, INFO, WARNING, ERROR).

## Testing

The application includes a comprehensive test suite using pytest.

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_document_loading.py

# Run specific test class
pytest tests/test_document_loading.py::TestDocumentLoading

# Run with coverage report
pytest --cov=app --cov-report=html

# Run with coverage and see missing lines
pytest --cov=app --cov-report=term-missing
```

### Test Coverage

**Current Coverage: 61%** (77 tests)

The test suite covers:
- ✅ Document loading from uploaded files (PDF, DOCX, TXT)
- ✅ Document metadata handling
- ✅ Vector store creation with MongoDB
- ✅ Document chunking and splitting
- ✅ Conversation chain creation
- ✅ RAG chain function execution (format_docs, create_rag_chain_input)
- ✅ Error handling and edge cases
- ✅ Integration workflows
- ✅ Configuration handling (database, collection, index names)
- ✅ File cleanup and temporary file handling
- ✅ Unsupported file type handling

### Test Structure

- `tests/test_document_loading.py` - Document loading functionality tests (PDF, DOCX, TXT)
- `tests/test_document_loading_edge_cases.py` - Edge cases for document loading
- `tests/test_vector_store.py` - MongoDB vector store tests
- `tests/test_vector_store_extended.py` - Extended vector store tests
- `tests/test_conversation_chain.py` - Conversation chain tests
- `tests/test_conversation_chain_extended.py` - Extended conversation chain tests
- `tests/test_rag_chain_functions.py` - RAG chain internal function tests
- `tests/test_rag_chain_invocation.py` - RAG chain invocation tests
- `tests/test_integration.py` - Integration tests
- `tests/test_integration_extended.py` - Extended integration tests
- `tests/test_error_handling.py` - Error handling tests
- `tests/test_configuration.py` - Configuration and database name tests
- `tests/test_processing_workflow.py` - Processing workflow tests
- `tests/test_session_state.py` - Session state handling tests
- `tests/test_utils.py` - Utility and helper function tests
- `tests/conftest.py` - Pytest fixtures and configuration

For more details, see [tests/README.md](tests/README.md).

## Requirements

- Python 3.8+
- OpenAI API key
- MongoDB Atlas account and connection string
- Required packages listed in `requirements.txt`

