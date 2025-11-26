# Test Suite for PDF RAG Application

This directory contains unit tests for the PDF RAG application.

## Test Structure

- `test_pdf_loading.py` - Tests for PDF loading functionality
- `test_vector_store.py` - Tests for MongoDB vector store creation
- `test_conversation_chain.py` - Tests for conversation chain creation
- `test_integration.py` - Integration tests for complete workflows
- `test_utils.py` - Utility tests and helper functions
- `conftest.py` - Pytest fixtures and configuration

## Running Tests

### Run all tests:
```bash
pytest
```

### Run specific test file:
```bash
pytest tests/test_pdf_loading.py
```

### Run with verbose output:
```bash
pytest -v
```

### Run with coverage:
```bash
pytest --cov=app --cov-report=html
```

### Run specific test class:
```bash
pytest tests/test_pdf_loading.py::TestPDFLoading
```

### Run specific test function:
```bash
pytest tests/test_pdf_loading.py::TestPDFLoading::test_load_single_pdf_success
```

## Test Coverage

The test suite covers:
- ✅ PDF loading from uploaded files
- ✅ Document metadata handling
- ✅ Vector store creation with MongoDB
- ✅ Document chunking and splitting
- ✅ Conversation chain creation
- ✅ Error handling and edge cases
- ✅ Integration workflows

## Mocking

Tests use extensive mocking to avoid:
- Actual API calls to OpenAI
- Real MongoDB connections
- File system operations
- Streamlit UI components

## Adding New Tests

When adding new functionality:
1. Create corresponding test file or add to existing one
2. Follow naming convention: `test_*.py`
3. Use descriptive test names: `test_<functionality>_<scenario>`
4. Add appropriate fixtures in `conftest.py` if needed
5. Mock external dependencies

