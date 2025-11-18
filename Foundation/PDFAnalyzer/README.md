# PDF Document Ingestion System

A comprehensive system for ingesting PDF documents into a Vector MongoDB database with page-wise chunking and semantic search capabilities.

## Features

- **PDF Text Extraction**: Extract text from PDF files page by page
- **Intelligent Chunking**: Split documents into overlapping chunks with configurable size and overlap
- **Vector Embeddings**: Generate semantic embeddings using sentence transformers or Azure OpenAI
- **MongoDB Storage**: Store chunks with embeddings in MongoDB for efficient retrieval
- **Batch Processing**: Process multiple PDF files in batches
- **Comprehensive Logging**: Detailed logging and statistics tracking
- **Error Handling**: Robust error handling with detailed error reporting
- **Azure OpenAI Integration**: Support for Azure OpenAI embedding models
- **Hybrid Embedding Support**: Choose between local sentence-transformers or cloud-based Azure OpenAI

## Installation

1. **Create and activate virtual environment**:
   ```bash
   # Create virtual environment (if not already created)
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

2. **Install Python dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and start MongoDB**:
   - Install MongoDB Community Edition
   - Start MongoDB service:
     ```bash
     # On macOS with Homebrew
     brew services start mongodb-community
     
     # On Ubuntu/Debian
     sudo systemctl start mongod
     
     # On Windows
     net start MongoDB
     ```

4. **Configure Azure OpenAI (Optional)**:
   - Set up Azure OpenAI resource in Azure Portal
   - Deploy embedding model (e.g., `text-embedding-ada-002`)
   - Set environment variables:
     ```bash
     export USE_AZURE_OPENAI="true"
     export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
     export AZURE_OPENAI_API_KEY="your-api-key-here"
     export AZURE_EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002"
     ```

## Quick Start

Follow these steps to get the application running quickly:

1. **Activate the virtual environment**:
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

2. **Configure your environment** (optional):
   - Edit `env.txt` to set your MongoDB connection string and Azure OpenAI credentials
   - The default configuration uses a cloud MongoDB instance and Azure OpenAI

3. **Add PDF files**:
   - Place your PDF files in the `PDF/` folder
   - The system will process all `.pdf` files in this directory

4. **Run the application**:
   ```bash
   # Using run.py (recommended - loads environment from env.txt):
   python run.py
   
   # Or using main.py directly:
   python main.py
   ```

5. **Check results**:
   - View processing logs in `ingestion.log`
   - Check statistics in `ingestion_stats.json`
   - Your documents are now stored in MongoDB with vector embeddings

## Usage

### Basic Usage

**Recommended approach** - Process all PDF files using `run.py` (loads environment from `env.txt`):

```bash
# Make sure virtual environment is activated
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate     # On Windows

# Run the application
python run.py
```

**Alternative approach** - Process all PDF files using `main.py` directly:

```bash
python main.py
```

### Advanced Usage

```bash
# Specify custom PDF folder
python main.py --pdf-folder /path/to/your/pdfs

# Custom MongoDB connection
python main.py --mongodb-uri "mongodb://localhost:27017/"

# Custom chunk size and overlap
python main.py --chunk-size 1500 --chunk-overlap 300

# Force reprocess all files
python main.py --force-reprocess

# Verbose output
python main.py --verbose

# Use Azure OpenAI for embeddings
python main.py --use-azure-openai
```

### Command Line Options

- `--pdf-folder`: Path to folder containing PDF files (default: ./PDF)
- `--mongodb-uri`: MongoDB connection URI (default: mongodb://localhost:27017/)
- `--database-name`: MongoDB database name (default: rag_documents)
- `--chunk-size`: Maximum characters per chunk (default: 1000)
- `--chunk-overlap`: Character overlap between chunks (default: 200)
- `--batch-size`: Number of chunks to process in each batch (default: 50)
- `--force-reprocess`: Force reprocessing of all files
- `--verbose`: Enable verbose logging
- `--stats-file`: Output file for processing statistics
- `--use-azure-openai`: Use Azure OpenAI for embeddings instead of sentence-transformers

## Configuration

### Environment Configuration

The application uses `env.txt` for configuration. Create env.txt file by referring the below keys/the keys from env-sample.txt.
This file contains all the necessary environment variables:

```bash
# MongoDB Configuration
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
DATABASE_NAME=your_database_name
COLLECTION_NAME=your_collection_name

# PDF Processing Configuration
PDF_FOLDER=./PDF
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
BATCH_SIZE=50

# Embedding Configuration
USE_AZURE_OPENAI=true

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT_NAME=gpt-4o-mini
AZURE_EMBEDDING_DEPLOYMENT_NAME=text-embedding-ada-002
```

### Alternative Configuration Methods

You can also customize the system by modifying `config.py` or setting environment variables:

```bash
export MONGODB_URI="mongodb://localhost:27017/"
export DATABASE_NAME="my_rag_database"
export CHUNK_SIZE="1500"
export CHUNK_OVERLAP="300"

# For Azure OpenAI
export USE_AZURE_OPENAI="true"
export AZURE_OPENAI_ENDPOINT="https://your-resource.openai.azure.com/"
export AZURE_OPENAI_API_KEY="your-api-key-here"
export AZURE_EMBEDDING_DEPLOYMENT_NAME="text-embedding-ada-002"
```

## Project Structure

```
Data Ingestion/
├── PDF/                          # PDF files to process
│   └── 1 Generative Adversarial Nets.pdf.. etc
├── main.py                       # Main execution script
├── run.py                        # Script to run main.py with env.txt configuration
├── env.txt                       # Environment configuration file
├── ingestion_pipeline.py         # Main ingestion pipeline
├── database.py                   # MongoDB vector database operations
├── pdf_processor.py              # PDF text extraction and chunking
├── config.py                     # Configuration settings
├── requirements.txt              # Python dependencies
├── README.md                     # This file
├── venv/                         # Virtual environment directory
├── ingestion.log                 # Processing logs (generated)
└── ingestion_stats.json          # Processing statistics (generated)
```

## How It Works

1. **PDF Processing**: The system scans the PDF folder for `.pdf` files
2. **Text Extraction**: Each PDF is processed page by page using PyPDF2
3. **Text Cleaning**: Extracted text is cleaned and preprocessed
4. **Chunking**: Text is split into overlapping chunks with configurable size
5. **Embedding Generation**: Each chunk is converted to a vector embedding using sentence transformers
6. **Database Storage**: Chunks and embeddings are stored in MongoDB with metadata
7. **Indexing**: Database indexes are created for efficient searching

## Database Schema

Each document chunk is stored with the following structure:

```json
{
  "_id": "ObjectId",
  "document_id": "unique_document_identifier",
  "document_name": "filename.pdf",
  "document_path": "/path/to/file.pdf",
  "page_number": 1,
  "chunk_index": 0,
  "global_chunk_index": 0,
  "text": "chunk text content",
  "embedding": [0.1, 0.2, ...],  // 384-dimensional vector
  "char_count": 1000,
  "word_count": 150,
  "is_complete_page": false
}
```

## Search Capabilities

The system supports both vector similarity search and text search:

- **Vector Search**: Semantic similarity using embeddings
- **Text Search**: Full-text search using MongoDB's text index
- **Filtering**: Filter by document ID, page number, or other metadata

## Monitoring and Logging

- **Logs**: Detailed processing logs saved to `ingestion.log`
- **Statistics**: Processing statistics saved to `ingestion_stats.json`
- **Progress**: Real-time progress tracking with tqdm
- **Error Reporting**: Comprehensive error reporting for failed files

## Performance Considerations

- **Batch Processing**: Chunks are processed in configurable batches for efficiency
- **Memory Management**: Large files are processed page by page to manage memory
- **Database Indexing**: Optimized indexes for fast retrieval
- **Embedding Caching**: Embeddings are generated efficiently using sentence transformers

## Troubleshooting

### Common Issues

1. **MongoDB Connection Failed**:
   - Ensure MongoDB is running
   - Check connection string
   - Verify network connectivity

2. **PDF Processing Errors**:
   - Check if PDF files are not corrupted
   - Ensure files are readable
   - Check file permissions

3. **Memory Issues**:
   - Reduce batch size
   - Process files individually
   - Increase system memory

4. **Embedding Model Download**:
   - First run may take time to download the model
   - Ensure internet connectivity
   - Check available disk space

### Logs

Check `ingestion.log` for detailed error messages and processing information.

## Dependencies

- `pymongo`: MongoDB Python driver
- `sentence-transformers`: Text embedding generation
- `PyPDF2`: PDF text extraction
- `numpy`: Numerical operations
- `tqdm`: Progress bars
- `python-dotenv`: Environment variable management

## License

This project is open source and available under the MIT License.
