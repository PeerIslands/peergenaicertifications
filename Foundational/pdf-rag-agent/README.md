# RAG-Based PDF Assistant Chatbot

This is an AI chatbot that helps users by answering their questions using uploaded PDF files. It uses RAG (Retrieval-Augmented Generation) & Google’s Gemini API to find and provide relevant answers from the documents.

## How We Collected Data

To make this chatbot useful:

- We visited 20 different university websites in Pakistan and copied their FAQs (Frequently Asked Questions).
- We also asked students to fill out a form with their own questions.
- We combined all these questions and answers into one PDF.
- This PDF was used by the chatbot to answer questions.

## What This Chatbot Can Do

- Reads PDF files like brochures, admission guides, and FAQs.
- Understands student questions.
- Gives quick and smart answers using AI.

## Features

- Upload university-related PDF documents (in our case -> university_faq.pdf)
- Breaks the PDF into small parts for better understanding.
- Turns those parts into a format that AI can understand.
- Finds the best parts of the PDF related to your question.
- Gives a short and helpful answer using Google's Gemini AI.
- Easy-to-use web app made with Streamlit.

## Tools and Technologies Used

- Python
- LangChain
- Streamlit
- PDFPlumber
- NumPy
- scikit-learn
- Google Gemini API

## Architecture & Data Flow

### Overview

The RAG (Retrieval-Augmented Generation) agent works in two main phases:

1. **Indexing Phase**: Processing and storing PDF content with embeddings
2. **Query Phase**: Retrieving relevant context and generating answers

### Complete Data Flow

```
PDF Upload
    ↓
Load PDF (PDFPlumberLoader)
    ↓
Split into Chunks (RecursiveCharacterTextSplitter)
    ├─ Chunk Size: 1000 characters
    └─ Overlap: 200 characters
    ↓
Generate Embeddings (Gemini Embedding API)
    ├─ Each chunk → 768-dimensional vector
    └─ Store in documents_store
    ↓
User Question
    ↓
Generate Query Embedding (Gemini Embedding API)
    ↓
Retrieve Similar Documents (Cosine Similarity)
    ├─ Calculate similarity scores
    └─ Return top-3 most relevant chunks
    ↓
Format Context
    ↓
Generate Answer (Gemini Chat API)
    ↓
Display Answer
```

## How It Works

1. Upload a PDF file (for example: university FAQs).
2. The chatbot reads and splits the content into small parts.
3. You type a question (for example: " I have DAE background. Which programmes can I apply for? ").
4. The chatbot finds the most relevant parts from the PDF.
5. It uses those parts to give a short and correct answer.

## Code Architecture & Function Overview

### Core Components

#### 1. **Embedding Generation** (`get_gemini_embedding()`)

- **Purpose**: Converts text into numerical vectors (embeddings) that represent semantic meaning
- **Input**: Text string (up to 1000 characters)
- **Output**: 768-dimensional NumPy array
- **API Used**: Google Gemini Embedding API
- **Key Features**:
  - Robust response parsing with fallback mechanisms
  - Handles multiple response formats from Gemini API
  - Error handling with user warnings

#### 2. **PDF Processing**

- **`upload_pdf(file)`**: Saves uploaded PDF to `chat-with-pdf/pdfs/` directory
- **`load_pdf(file_path)`**: Uses PDFPlumberLoader to extract text from PDF
- **`split_text(documents)`**: Chunks documents with:
  - 1000-character chunks for optimal semantic segments
  - 200-character overlap for context continuity

#### 3. **Document Indexing** (`index_documents()`)

- **Purpose**: Creates searchable vector store
- **Process**:
  1. Iterate through all document chunks
  2. Generate embedding for each chunk
  3. Store `{content, embedding}` pairs in memory
  4. Return count of indexed documents
- **Storage**: In-memory Python list (documents_store)

#### 4. **Retrieval** (`retrieve_relevant_docs()`)

- **Purpose**: Finds the most relevant document chunks for a query
- **Process**:
  1. Generate embedding for user query
  2. Calculate cosine similarity between query and all stored embeddings
  3. Sort by similarity score (descending)
  4. Return top-k (default: 3) most similar chunks
- **Uses**: scikit-learn's cosine_similarity function
- **Why Cosine Similarity**: Measures angle between vectors, perfect for semantic similarity

#### 5. **Answer Generation** (`answer_question_with_gemini()`)

- **Purpose**: Generates concise answers using retrieved context
- **Process**:
  1. Format prompt with template (question + context)
  2. Send to Gemini Chat API
  3. Parse response with multiple fallback strategies
  4. Return generated answer (max 3 sentences)
- **Prompt Template**: Instructs AI to use context and be concise

#### 6. **Streamlit UI** (Main Application)

- **File Upload**: Accepts PDF files
- **Processing Pipeline**: Automatically processes uploaded PDF
- **Chat Interface**:
  - Displays user questions
  - Shows AI-generated answers
  - Uses Streamlit's chat components for UX

### Data Storage

**In-Memory Vector Store** (`documents_store`)

- Structure: List of dictionaries

```python
[
    {
        "content": "chunk text here...",
        "embedding": [0.123, -0.456, ...]  # 768 dimensions
    },
    ...
]
```

- Limitations: Resets when app restarts
- Suitable for: Single-session interactions, demos

### API Integration

**Google Gemini APIs Used**:

1. **Embedding API** (`gemini-embedding-001`)

   - Converts text to vectors
   - Used twice per interaction (query + context generation)

2. **Chat API** (`gemini-2.0-flash`)
   - Generates natural language answers
   - Fast inference, suitable for chat

**Authentication**: API key stored in code (⚠️ should be moved to environment variables)

### How to run this

### 1. Clone the Repository

- git clone https://github.com/SohaibBazaz/rag-university-chatbot.git
- cd rag-university-chatbot

### 2. Install Libraries:

- pip install -r requirements.txt

### 3. Run the program:

- streamlit run pdf_assistant.py

## Configuration Parameters

Key parameters you can tune in `pdf_assistant.py`:

| Parameter           | Value                | Purpose                            |
| ------------------- | -------------------- | ---------------------------------- |
| `chunk_size`        | 1000                 | Characters per document chunk      |
| `chunk_overlap`     | 200                  | Overlap between chunks for context |
| `top_k`             | 3                    | Number of retrieved documents      |
| `max_answer_length` | 3 sentences          | Maximum answer length              |
| `embedding_model`   | gemini-embedding-001 | Embedding model                    |
| `chat_model`        | gemini-2.0-flash     | LLM model for answers              |

## Performance Considerations

- **Embedding Generation**: ~1-2 seconds per chunk
- **Similarity Search**: O(n) where n = number of indexed chunks
- **Memory Usage**: ~1KB per embedding + content
- **API Costs**: Google Gemini API pay-as-you-go pricing

## Troubleshooting

| Issue                                           | Solution                                           |
| ----------------------------------------------- | -------------------------------------------------- |
| "Couldn't parse embedding from Gemini response" | Check API key validity, verify internet connection |
| No relevant answers found                       | Ensure PDF content matches question domain         |
| Slow performance                                | Reduce chunk_size or decrease number of chunks     |
| App crashes                                     | Check PDF file format (must be valid PDF)          |

## Security Notes

⚠️ **Important**: The API key is currently hardcoded in `pdf_assistant.py`.
**For production**, move it to environment variables:

```bash
export GEMINI_API_KEY="your_key_here"
```

Then use:

```python
API_KEY = os.getenv("GEMINI_API_KEY")
```

## Additional Features to be Added

- Add human support when the AI can't answer.
- Add voice support so users can speak their questions.
- Persistent database storage instead of in-memory storage
- Multi-PDF support with document metadata
- Answer confidence scores
- Chat history and session management
