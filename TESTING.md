# Test Documentation - RAG Chat Application

This document provides comprehensive information about the test suite for the RAG Chat Application, including both frontend and backend testing strategies.

## Overview

The RAG Chat Application includes a comprehensive test suite covering:
- **Backend Tests**: Unit tests for services, routes, and models
- **Frontend Tests**: Component tests, integration tests, and API service tests
- **Integration Tests**: End-to-end testing of the complete application flow

## Test Structure

### Backend Tests

Located in `backend-rag-chat/tests/`:

```
tests/
├── __init__.py
├── test_services.py      # Service layer tests
└── test_routes.py        # API route tests
```

#### Test Categories

1. **Service Tests** (`test_services.py`):
   - `TestEmbeddingService`: Tests for embedding generation
   - `TestVectorStore`: Tests for vector database operations
   - `TestFileProcessor`: Tests for PDF processing and chunking
   - `TestRAGPipeline`: Tests for RAG response generation
   - `TestConversationMemory`: Tests for conversation history management
   - `TestModels`: Tests for Pydantic data models

2. **Route Tests** (`test_routes.py`):
   - `TestChatRoutes`: Tests for chat API endpoints
   - `TestDocumentRoutes`: Tests for document management endpoints
   - `TestMainApp`: Tests for FastAPI application configuration
   - `TestIntegration`: Integration tests for complete workflows

### Frontend Tests

Located in `frontend-rag-chat/src/__tests__/`:

```
src/__tests__/
├── App.test.js           # Main application tests
├── ChatWindow.test.js    # Chat display component tests
├── ChatInput.test.js     # Chat input component tests
└── api.test.js           # API service tests
```

#### Test Categories

1. **Component Tests**:
   - `App.test.js`: Main application state management and routing
   - `ChatWindow.test.js`: Message display and rendering
   - `ChatInput.test.js`: User input handling and form submission

2. **Service Tests**:
   - `api.test.js`: API communication and error handling

## Running Tests

### Quick Start

Run all tests with the provided script:

```bash
./run_tests.sh
```

### Individual Test Commands

#### Backend Tests

```bash
cd backend-rag-chat
source .venv/bin/activate
pytest tests/ -v
```

With coverage:
```bash
pytest tests/ -v --cov=. --cov-report=html
```

#### Frontend Tests

```bash
cd frontend-rag-chat
npm test
```

With coverage:
```bash
npm run test:coverage
```

### Test Script Options

The `run_tests.sh` script supports several options:

```bash
./run_tests.sh --backend-only    # Run only backend tests
./run_tests.sh --frontend-only   # Run only frontend tests
./run_tests.sh --integration     # Run integration tests
./run_tests.sh --no-report       # Skip generating test report
./run_tests.sh --help            # Show help
```

## Test Coverage

### Coverage Goals

- **Backend**: Minimum 80% code coverage
- **Frontend**: Minimum 80% code coverage
- **Critical Paths**: 100% coverage for core RAG functionality

### Coverage Reports

After running tests, coverage reports are generated:

- **Backend**: `backend-rag-chat/htmlcov/index.html`
- **Frontend**: `frontend-rag-chat/coverage/lcov-report/index.html`

## Test Categories

### Unit Tests

#### Backend Unit Tests

1. **EmbeddingService Tests**:
   - Embedding generation for single and multiple texts
   - Dimension validation
   - Error handling for invalid inputs

2. **VectorStore Tests**:
   - Document storage and retrieval
   - Vector similarity search
   - Index creation and management
   - Database operations (CRUD)

3. **FileProcessor Tests**:
   - PDF file discovery and processing
   - Text chunking and metadata extraction
   - Error handling for corrupted files

4. **RAGPipeline Tests**:
   - Context building from retrieved chunks
   - Prompt generation with conversation history
   - Response generation and source extraction

5. **ConversationMemory Tests**:
   - Message storage and retrieval
   - Session management
   - Context formatting for LLM

#### Frontend Unit Tests

1. **Component Tests**:
   - Rendering with different props
   - User interaction handling
   - State management
   - Error boundary behavior

2. **API Service Tests**:
   - HTTP request/response handling
   - Error handling and retry logic
   - Request timeout handling
   - Response data validation

### Integration Tests

1. **Backend Integration**:
   - Complete RAG pipeline flow
   - File processing to vector storage
   - API endpoint integration
   - Database operations

2. **Frontend Integration**:
   - Component interaction
   - API communication
   - State synchronization
   - Error propagation

3. **End-to-End Tests**:
   - Complete user workflows
   - Cross-service communication
   - Error handling across layers

## Mocking Strategy

### Backend Mocking

- **External Services**: MongoDB, Ollama API, HuggingFace models
- **File System**: PDF files and directory operations
- **Network Requests**: HTTP calls to external APIs
- **Async Operations**: Database operations and API calls

### Frontend Mocking

- **API Calls**: Axios requests to backend
- **External Libraries**: React Testing Library utilities
- **Browser APIs**: Local storage, fetch, etc.
- **Component Dependencies**: Child components and hooks

## Test Data

### Backend Test Data

- **Sample PDFs**: Mock PDF documents for processing tests
- **Embedding Vectors**: Pre-computed embeddings for similarity tests
- **Database Records**: Sample document chunks and metadata
- **API Responses**: Mock responses from external services

### Frontend Test Data

- **Sample Messages**: Chat messages with different formats
- **API Responses**: Mock API responses for different scenarios
- **User Inputs**: Various user input patterns and edge cases
- **Error States**: Different error conditions and messages

## Continuous Integration

### GitHub Actions (Recommended)

Create `.github/workflows/test.yml`:

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        cd backend-rag-chat
        python -m venv .venv
        source .venv/bin/activate
        pip install -r requirements.txt
    - name: Run tests
      run: |
        cd backend-rag-chat
        source .venv/bin/activate
        pytest tests/ --cov=. --cov-report=xml

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    - name: Install dependencies
      run: |
        cd frontend-rag-chat
        npm install
    - name: Run tests
      run: |
        cd frontend-rag-chat
        npm run test:ci
```

## Best Practices

### Test Writing Guidelines

1. **Naming Convention**:
   - Test files: `test_*.py` (backend), `*.test.js` (frontend)
   - Test functions: `test_*` (backend), descriptive names (frontend)
   - Test classes: `Test*` (backend)

2. **Test Structure**:
   - Arrange-Act-Assert pattern
   - Clear test descriptions
   - Single responsibility per test
   - Independent tests (no dependencies)

3. **Mocking Guidelines**:
   - Mock external dependencies
   - Use realistic test data
   - Verify mock interactions
   - Clean up after tests

4. **Error Testing**:
   - Test error conditions
   - Verify error messages
   - Test error recovery
   - Validate error handling

### Performance Considerations

1. **Test Speed**:
   - Use mocks for slow operations
   - Parallel test execution
   - Efficient test data setup
   - Minimal database operations

2. **Resource Management**:
   - Clean up test resources
   - Use test-specific databases
   - Limit test data size
   - Monitor memory usage

## Troubleshooting

### Common Issues

1. **Backend Test Issues**:
   - MongoDB connection errors: Use test database
   - Missing dependencies: Check requirements.txt
   - Async test failures: Use pytest-asyncio
   - Import errors: Check PYTHONPATH

2. **Frontend Test Issues**:
   - Component not found: Check import paths
   - Mock not working: Verify mock setup
   - Async operations: Use waitFor
   - Environment variables: Check .env files

### Debug Commands

```bash
# Backend debugging
pytest tests/ -v -s --tb=long
pytest tests/test_services.py::TestEmbeddingService::test_generate_embedding -v

# Frontend debugging
npm test -- --verbose
npm test -- --watch
```

## Future Enhancements

### Planned Improvements

1. **Performance Tests**:
   - Load testing for API endpoints
   - Memory usage monitoring
   - Response time benchmarks

2. **Security Tests**:
   - Input validation testing
   - Authentication/authorization tests
   - SQL injection prevention

3. **Accessibility Tests**:
   - Screen reader compatibility
   - Keyboard navigation
   - Color contrast validation

4. **Visual Regression Tests**:
   - UI component snapshots
   - Cross-browser compatibility
   - Responsive design testing

## Conclusion

This comprehensive test suite ensures the reliability and maintainability of the RAG Chat Application. Regular test execution and coverage monitoring help maintain code quality and catch regressions early in the development process.

For questions or issues with the test suite, please refer to the troubleshooting section or create an issue in the project repository.
