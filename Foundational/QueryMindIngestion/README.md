# PDF Ingestion Tool

A Python tool for reading PDF files, chunking text using LangChain, storing data in MongoDB, and generating embeddings using Ollama.

## Features

- **PDF Reading**: Extract text content from PDF files in a specified folder
- **Text Chunking**: Split PDF text into manageable chunks using LangChain's RecursiveCharacterTextSplitter
- **MongoDB Storage**: Store chunked data as separate documents in MongoDB
- **Embedding Generation**: Generate embeddings for each chunk using Ollama's embeddinggemma model
- **Configurable**: All settings can be configured via environment variables or config file

## Prerequisites

1. **Python 3.8+**
2. **MongoDB** running locally or accessible via URI
3. **Ollama** running locally with the `embeddinggemma` model installed

### Installing Ollama and the Embedding Model

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.ai/install.sh | sh

# Pull the embedding model
ollama pull embeddinggemma
```

## Installation

1. Clone or download this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Configuration

The tool uses environment variables for configuration. You can set these in your environment or create a `.env` file:

```bash
# PDF folder path (absolute or relative path)
PDF_FOLDER_PATH=./pdfs

# MongoDB configuration
MONGODB_URI=mongodb+srv://mongosh_aj:ajinkya123@cluster0.clx9fur.mongodb.net/
MONGODB_DATABASE=query-mind
MONGODB_COLLECTION=knowledge-base

# Ollama configuration
OLLAMA_BASE_URL=http://localhost:11434
EMBEDDING_MODEL=embeddinggemma

# Chunking configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

## Usage

### Basic Usage

1. **Place PDF files** in the configured folder (default: `./pdfs/`)
2. **Run the tool**:

```bash
python pdf_ingestion_tool.py
```

### Programmatic Usage

```python
from pdf_ingestion_tool import PDFIngestionTool

# Initialize the tool
tool = PDFIngestionTool()

# Test connections
if tool.test_connections():
    # Process all PDFs
    results = tool.process_all_pdfs()
    print(f"Processed {results['total_files_processed']} files")
    
    # Get statistics
    stats = tool.get_processing_stats()
    print(f"Total chunks: {stats['total_chunks']}")
    
    # Clean up connections
    tool.close_connections()
```

### Individual Component Usage

You can also use individual components:

```python
from pdf_reader import PDFReader
from text_chunker import TextChunker
from mongodb_client import MongoDBClient
from embedding_generator import EmbeddingGenerator

# Read PDFs
reader = PDFReader("./my_pdfs")
pdf_data = reader.read_all_pdfs()

# Chunk text
chunker = TextChunker(chunk_size=500, chunk_overlap=100)
chunks = chunker.chunk_pdf_data(pdf_data[0])

# Store in MongoDB
mongo = MongoDBClient()
mongo.insert_chunks(chunks)

# Generate embeddings
embedder = EmbeddingGenerator()
embeddings = embedder.generate_embeddings_batch([chunk["chunk_text"] for chunk in chunks])
```

## MongoDB Document Structure

Each chunk is stored as a separate document with the following structure:

```json
{
  "_id": "ObjectId",
  "chunk_index": 0,
  "chunk_text": "The actual text content...",
  "chunk_size": 1000,
  "metadata": {
    "source_file": "document.pdf",
    "source_path": "/path/to/document.pdf",
    "total_pages": 10,
    "pdf_metadata": {
      "title": "Document Title",
      "author": "Author Name",
      "creator": "PDF Creator",
      "creation_date": "2024-01-01"
    }
  },
  "embedding": [0.1, 0.2, 0.3, ...]  // Vector of floats
}
```

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Ensure MongoDB is running: `mongod`
   - Check the `MONGODB_URI` in your configuration

2. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Verify the model is installed: `ollama list`
   - Check the `OLLAMA_BASE_URL` in your configuration

3. **PDF Reading Error**
   - Ensure PDF files are not corrupted
   - Check file permissions
   - Verify the `PDF_FOLDER_PATH` exists and contains PDF files

4. **Memory Issues**
   - Reduce `CHUNK_SIZE` for large PDFs
   - Process PDFs one at a time for very large files

### Testing Individual Components

```python
# Test PDF reading
from pdf_reader import PDFReader
reader = PDFReader()
pdf_files = reader.get_pdf_files()
print(f"Found {len(pdf_files)} PDF files")

# Test MongoDB connection
from mongodb_client import MongoDBClient
mongo = MongoDBClient()
print("MongoDB connected:", mongo.test_connection())

# Test Ollama connection
from embedding_generator import EmbeddingGenerator
embedder = EmbeddingGenerator()
print("Ollama connected:", embedder.test_connection())
```

## File Structure

```
QueryMindIngestion/
├── pdf_ingestion_tool.py    # Main orchestration tool
├── pdf_reader.py           # PDF reading functionality
├── text_chunker.py         # Text chunking with LangChain
├── mongodb_client.py       # MongoDB operations
├── embedding_generator.py  # Ollama embedding generation
├── config.py              # Configuration management
├── requirements.txt       # Python dependencies
├── README.md             # This file
└── pdfs/                 # Folder for PDF files (created automatically)
```

## Dependencies

- `langchain`: Text chunking and LLM integration
- `langchain-community`: Community integrations including Ollama
- `pymongo`: MongoDB driver
- `PyPDF2`: PDF text extraction
- `python-dotenv`: Environment variable management
- `pydantic`: Data validation and settings
- `ollama`: Ollama API client

## License

This project is open source. Feel free to modify and distribute as needed.
