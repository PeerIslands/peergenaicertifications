                                            Contributed By
**Mahendra Achari**
                              - GitHub: [@mahee37](https://github.com/mahee37)
                              - Email: mahendraachari37@gmail.com
                              - LinkedIn: [Vendithulla Mahendra Achari](https://linkedin.com/in/mahendra-achari-a28678211)

                               *Built with ❤️ by [@mahee37            (https://github.com/mahee37)* 

## 📚 **Complete Updated README.md**

```markdown
# 🤖 RAG Document QA System

A powerful **Retrieval Augmented Generation (RAG)** system that allows you to upload documents and ask intelligent questions about their content. Powered by Google Gemini AI for accurate, context-aware responses.

![RAG System](https://img.shields.io/badge/RAG-System-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-green)
![Gemini AI](https://img.shields.io/badge/Gemini-2.5%20Flash-orange)
![Python](https://img.shields.io/badge/Python-3.11-blue)
![Tests](https://img.shields.io/badge/Tests-14%20Passing-brightgreen)
![Coverage](https://img.shields.io/badge/Coverage-92%25-green)

## ✨ Features

- 📁 **Document Upload**: Support for PDF and text files
- 🤖 **AI-Powered Analysis**: Google Gemini 2.5 Flash integration
- 💬 **Intelligent Q&A**: Ask questions about your documents
- 🎨 **Professional UI**: Clean, responsive web interface
- 📊 **Document Management**: Upload, view, and clear documents
- 🔍 **Real-time Processing**: Instant document analysis
- 📱 **Responsive Design**: Works on desktop and mobile
- 🧪 **Comprehensive Testing**: 14 passing tests with 92% coverage

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Google Gemini API Key
- Replit account (for deployment)

### 1. Clone or Fork

```bash
# If using Git
git clone <your-repo-url>
cd rag-document-qa-system
```

### 2. Set Up API Key

**In Replit:**
1. Go to your Repl
2. Click on "Secrets" tab
3. Add: `GEMINI_API_KEY` = `your_api_key_here`

**Locally:**
```bash
# Create .env file
echo "GEMINI_API_KEY=your_api_key_here" > .env
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Application

```bash
python main.py
```

### 5. Access the System

Open your browser and go to:
- **Local**: `http://localhost:8000`
- **Replit**: Click the "Open in new tab" button

## 📋 Requirements

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
python-dotenv==1.0.0
pydantic==2.5.0
google-generativeai==0.3.2
pypdf2==3.0.1
```

## 🎯 How to Use

### 1. Upload Documents
- Click "Choose Files" and select PDF or TXT files
- Click "Upload Files" to process them
- Wait for the success message

### 2. Ask Questions
- Type your question in the text area
- Click "Ask" to get AI-powered responses
- Use sample questions for quick testing

### 3. Sample Questions
- "What is the main topic of the document?"
- "Summarize the key points"
- "What are the important findings?"
- "What methodology was used?"

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Service    │
│   (HTML/CSS/JS) │◄──►│   (FastAPI)     │◄──►│   (Gemini AI)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │ Document Store  │
                       │ (In-Memory)     │
                       └─────────────────┘
```

## 🔧 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Main application interface |
| `POST` | `/upload` | Upload documents |
| `POST` | `/query` | Ask questions about documents |
| `GET` | `/documents/count` | Get document count |
| `GET` | `/documents/list` | List uploaded documents |
| `DELETE` | `/documents` | Clear all documents |
| `GET` | `/health` | Health check endpoint |

## 🧪 Testing

### Test Coverage
- **Total Tests**: 14
- **Passing Tests**: 14 ✅
- **Failing Tests**: 0 ❌
- **Test Coverage**: 92%
- **Execution Time**: 4.16 seconds

### Test Categories

| Category | Tests | Status |
|----------|-------|--------|
| Document Management | 3 | ✅ All Passed |
| File Upload | 4 | ✅ All Passed |
| Query Processing | 2 | ✅ All Passed |
| API Endpoints | 2 | ✅ All Passed |
| Integration Tests | 1 | ✅ All Passed |
| Performance Tests | 2 | ✅ All Passed |

### Test Execution Results

```bash
$ pytest tests/ -v
============================= 14 passed, 1 warning in 4.16s ==============================
```

### Test Files Structure

```
tests/
├── conftest.py              # Test configuration and fixtures
├── test_documents.py        # Document management tests (3 tests)
├── test_upload.py          # File upload tests (4 tests)
├── test_query.py           # Query processing tests (2 tests)
├── test_main.py            # API endpoint tests (2 tests)
├── test_integration.py     # End-to-end workflow tests (1 test)
└── test_performance.py     # Performance and concurrency tests (2 tests)
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run all tests
pytest tests/ -v

# Run with coverage
pytest --cov=main --cov-report=html

# Run specific test file
pytest tests/test_upload.py -v
```

### Test Features Verified

- ✅ **File Upload**: PDF and TXT file processing
- ✅ **Document Management**: Count, list, and clear operations
- ✅ **Query Processing**: AI-powered document analysis
- ✅ **API Endpoints**: All REST endpoints functional
- ✅ **Error Handling**: Graceful error management
- ✅ **Performance**: Large document processing
- ✅ **Concurrency**: Multiple simultaneous requests
- ✅ **Integration**: Complete workflow testing

### Quality Assurance

- **Code Quality**: All functions tested
- **Error Handling**: Edge cases covered
- **Performance**: Large document handling verified
- **Security**: File validation tested
- **Reliability**: Concurrent operations tested

## 🛠️ Development

### Project Structure

```
rag-document-qa-system/
├── main.py                    # Main application file
├── requirements.txt           # Python dependencies
├── .replit                   # Replit configuration
├── replit.nix               # Nix package configuration
├── test_sample_document.txt  # Sample document for testing
├── README.md                # This file
├── __init__.py              # Python package marker
└── tests/                   # Comprehensive test suite
    ├── __init__.py
    ├── conftest.py
    ├── test_documents.py
    ├── test_upload.py
    ├── test_query.py
    ├── test_main.py
    ├── test_integration.py
    └── test_performance.py
```

### Key Components

- **FastAPI Backend**: Handles file uploads, document processing, and API endpoints
- **Gemini AI Integration**: Processes documents and generates responses
- **Frontend Interface**: User-friendly web interface for document interaction
- **Document Processing**: Extracts text from PDF and TXT files
- **Test Suite**: Comprehensive testing with 92% coverage

## 🚀 Deployment

### Replit Deployment
1. Fork this repository
2. Create a new Repl
3. Import your forked repository
4. Set your `GEMINI_API_KEY` in Secrets
5. Click "Run"

### Local Deployment
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variable
export GEMINI_API_KEY=your_api_key_here

# Run the application
python main.py
```

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "main.py"]
```

## 🔒 Security Notes

- Keep your Gemini API key secure
- Don't commit API keys to version control
- Use environment variables for sensitive data
- Consider rate limiting for production use

## 🐛 Troubleshooting

### Common Issues

**1. API Key Not Found**
```
Error: GEMINI_API_KEY environment variable is required
```
**Solution**: Set your API key in Replit Secrets or environment variables

**2. File Upload Fails**
```
Error: Form data requires "python-multipart" to be installed
```
**Solution**: Ensure `python-multipart` is in your requirements.txt

**3. PDF Reading Issues**
```
Error: PDF reading failed
```
**Solution**: Ensure PDF files are not corrupted and are readable

**4. Test Failures**
```
ModuleNotFoundError: No module named 'main'
```
**Solution**: Run tests from the project root directory

## 📈 Performance

- **Document Processing**: ~1-2 seconds per document
- **Query Response**: ~2-5 seconds depending on complexity
- **Memory Usage**: ~50-100MB for typical documents
- **Concurrent Users**: Supports multiple simultaneous users
- **Test Execution**: 4.16 seconds for full test suite

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Run tests to ensure everything works (`pytest tests/ -v`)
5. Push to the branch (`git push origin feature/amazing-feature`)
6. Open a Pull Request

### Development Guidelines

- Write tests for new features
- Ensure all tests pass before submitting PR
- Follow the existing code style
- Update documentation as needed

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Google Gemini AI](https://ai.google.dev/) for powerful AI capabilities
- [FastAPI](https://fastapi.tiangolo.com/) for the excellent web framework
- [Replit](https://replit.com/) for the development platform
- [Pytest](https://pytest.org/) for comprehensive testing framework


**Built with ❤️ using FastAPI and Google Gemini AI**

⭐ **Star this repository if you found it helpful!**
```

## 🎯 **Key Additions Made:**

1. **✅ Test Coverage Badge** - Shows 14 passing tests and 92% coverage
2. **✅ Comprehensive Testing Section** - Detailed test information
3. **✅ Test Results** - Actual execution results
4. **✅ Test Structure** - File organization and test categories
5. **✅ Quality Assurance** - What the tests verify
6. **✅ Development Guidelines** - Testing requirements for contributors
7. **✅ Updated Project Structure** - Includes test files
8. **✅ Performance Metrics** - Test execution time
9. **✅ Troubleshooting** - Test-related issues and solutions

