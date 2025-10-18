# AskMyPDF - RAG-Powered PDF Document Analysis

A full-stack PDF document analysis application with Retrieval-Augmented Generation (RAG) capabilities, built with React, Express, and LangChain.

## Features

- 🤖 **Hybrid RAG Search**: 75% Semantic + 25% BM25 keyword search
- 🧠 **LLM-based Query Expansion**: Intelligent query enhancement for better retrieval
- 💬 **Real-time Chat Interface**: Modern, responsive chat UI
- 📚 **Source Attribution**: View sources with search type indicators
- 💾 **Chat History**: MongoDB-based persistent storage
- 🔍 **Advanced Search**: MongoDB Atlas Vector Search + BM25 integration
- ⚙️ **Configurable Parameters**: Adjust model settings and document retrieval count
- ⚡ **Fast & Responsive**: Built with modern web technologies

## Tech Stack

### Frontend
- React 18 with TypeScript
- Tailwind CSS for styling
- Radix UI components
- React Query for state management
- Wouter for routing

### Backend
- Express.js with TypeScript
- LangChain for RAG implementation
- MongoDB with Atlas Vector Search
- BM25 for keyword search
- OpenAI API for embeddings and chat
- LLM-based query expansion for enhanced retrieval

## Prerequisites

1. **Node.js** (v18 or higher)
2. **MongoDB Atlas** account with vector search enabled
3. **OpenAI API Key**
4. **Vectorized Documents** in MongoDB collection

## Setup Instructions

### 1. Environment Configuration

Create a `.env` file in the root directory by copying the provided template:

```bash
cp .env-example .env
```

Then edit the `.env` file with your actual values.

> **Note**: The `.env-example` file contains all available environment variables with placeholder values. Only fill in the variables you need for your specific configuration.

#### **Required Environment Variables**

| Variable | Description | Example |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | `sk-...` |
| `MONGODB_URI` | MongoDB connection string | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `MONGODB_DATABASE` | Database name | `doc-analysis` |
| `MONGODB_COLLECTION` | Vectorized documents collection | `document_chunks` |
| `MONGODB_CHAT_HISTORY_COLLECTION` | Chat history collection | `chat_history` |

#### **Optional Environment Variables**

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_BASE_URL` | OpenAI API base URL | `https://api.openai.com/v1` |
| `OPENAI_API_VERSION` | API version (for Azure) | `2025-01-01-preview` |
| `AZURE_INSTANCE_NAME` | Azure instance name | `your-azure-instance` |
| `EMBEDDING_MODEL` | Embedding model name | `text-embedding-3-small` |
| `EMBEDDING_DEPLOYMENT_NAME` | Azure embedding deployment | `your-embedding-deployment` |
| `CHAT_MODEL` | Chat model name | `gpt-4o-mini` |
| `PORT` | Server port | `5001` |
| `NODE_ENV` | Environment mode | `development` |

#### **Configuration Examples**

**Standard OpenAI API:**
```bash
OPENAI_API_KEY=sk-your-openai-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
MONGODB_URI=mongodb+srv://user:pass@cluster.mongodb.net
MONGODB_DATABASE=doc-analysis
MONGODB_COLLECTION=document_chunks
```

**Azure OpenAI:**
```bash
OPENAI_API_KEY=your-azure-api-key
OPENAI_BASE_URL=https://your-resource.openai.azure.com/
OPENAI_API_VERSION=2025-01-01-preview
AZURE_INSTANCE_NAME=your-azure-instance
EMBEDDING_DEPLOYMENT_NAME=your-embedding-deployment
CHAT_MODEL=gpt-4o-mini
```

**Custom OpenAI-Compatible Endpoint:**
```bash
OPENAI_API_KEY=your-api-key
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

### 2. MongoDB Collections Setup

You need **2 MongoDB collections**:

#### Collection 1: Vectorized Documents
Your vectorized documents collection should have this structure:

```json
{
  "_id": "mongodb_object_id",
  "text": "Attention Is All You Need Ashish Vaswani Google Brain avaswani@google...",
  "page_number": 1,
  "chunk_index": 0,
  "char_count": 983,
  "word_count": 121,
  "is_complete_page": false,
  "document_id": "a458f3ff-184c-4017-96c0-0c516b91ed92",
  "document_name": "4 Attention is All You Need.pdf",
  "document_path": "PDF/4 Attention is All You Need.pdf",
  "global_chunk_index": 0,
  "embedding": [-0.036286670714616776, 0.017528537660837173, ...] // 1536-dimensional vector
}
```

#### Collection 2: Chat History (Auto-created)
The chat history collection will be automatically created with this structure:

```json
{
  "_id": "chat_history_id",
  "userId": "user_123",
  "query": "User's question",
  "response": "AI's response",
  "sources": [
    {
      "content": "Source content",
      "metadata": {...},
      "score": 0.85,
      "searchType": "semantic"
    }
  ],
  "createdAt": "2024-01-01T00:00:00Z"
}
```

**Create a Vector Search Index** in MongoDB Atlas:

1. Go to your Atlas cluster
2. Navigate to "Search" → "Create Index"
3. Choose "Vector Search"
4. Configure the index:

```json
{
  "fields": [
    {
      "type": "vector",
      "path": "embedding",
      "numDimensions": 1536,
      "similarity": "cosine"
    }
  ]
}
```

### 3. Installation

```bash
# Install dependencies
npm install

# Start development server
PORT=5001 npm run dev
```

The application will be available at `http://localhost:5001`

## API Endpoints

### Chat Endpoints

- `POST /api/chat` - Send a message and get RAG response
- `GET /api/chat/history/:userId` - Get user's chat history
- `GET /api/chat/history/entry/:id` - Get specific chat history entry by ID
- `GET /api/health` - Health check endpoint

### Example API Usage

```javascript
// Send a message with custom number of documents to retrieve
const response = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    query: "What is machine learning?",
    userId: "user_123",
    topK: 5 // Number of documents to retrieve (1-20)
  })
});

const data = await response.json();
console.log(data.answer); // RAG-generated response
console.log(data.sources); // Retrieved sources (up to topK documents)
```

## Project Structure

```
├── client/                 # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── services/       # API services
│   │   ├── pages/          # Page components
│   │   └── hooks/          # Custom hooks
├── server/                 # Express backend
│   ├── ragService.ts       # RAG implementation
│   ├── routes.ts           # API routes
│   ├── storage.ts          # Data storage
│   └── index.ts            # Server entry point
├── shared/                 # Shared types and schemas
└── package.json
```

## Hybrid RAG Implementation Details

The RAG system uses **Hybrid Search** with **Reciprocal Rank Fusion (RRF)** and **LLM-based Query Expansion**:

1. **Query Expansion** (Optional): LLM enhances user queries with synonyms and related terms
2. **Semantic Search**: MongoDB Atlas Vector Search for semantic similarity
3. **Keyword Search**: BM25 algorithm for exact keyword matching
4. **Reciprocal Rank Fusion**: Combines rankings from both search methods
5. **Embeddings**: OpenAI text-embedding-3-small for vector generation
6. **LLM**: OpenAI GPT models for response generation
7. **Context Assembly**: Retrieved documents are used as context for the LLM

### Query Expansion Feature

The system now includes intelligent query expansion that:
- Adds synonyms and alternative terms
- Includes related concepts and terminology
- Provides different ways to phrase the same question
- Incorporates technical terms that might be relevant

**Enable Query Expansion:**
```bash
# Add to your .env file
ENABLE_QUERY_EXPANSION=true
QUERY_EXPANSION_MODEL=gpt-4o-mini  # Optional: specify different model for expansion
```

### Hybrid RAG Flow

1. User sends a query
2. **Query Expansion** (if enabled):
   - LLM analyzes and expands the query with related terms
3. **Parallel Search Execution**:
   - Expanded query is embedded using OpenAI embeddings for semantic search
   - Expanded query is processed with BM25 for keyword search
4. **Reciprocal Rank Fusion**: 
   - Each search method produces a ranked list
   - RRF combines rankings using formula: `1 / (k + rank)`
   - Documents appearing in both lists get higher combined scores
4. **Document Retrieval**: Top-k documents are selected based on RRF scores
5. **Context Assembly**: Retrieved documents are used as context
6. **LLM Generation**: LLM generates response based on query + context
7. **Response**: Response and sources (with search type indicators) are returned

### RRF Benefits

- **Rank-based Combination**: More robust than score-based weighting
- **Handles Score Incompatibility**: Works even when different search methods use different score ranges
- **Promotes Consensus**: Documents ranked highly by both methods get boosted scores
- **Proven Effectiveness**: Widely used in information retrieval research

## Development

### Running in Development

```bash
# Start with hot reload
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

### Code Quality

```bash
# Type checking
npm run check

# Database operations
npm run db:push
```

## Configuration

### RAG Service Configuration

The RAG service can be configured via environment variables:

- `EMBEDDING_MODEL`: OpenAI embedding model (default: text-embedding-3-small)
- `CHAT_MODEL`: OpenAI chat model (default: gpt-3.5-turbo)
- `MONGODB_COLLECTION`: Name of your vectorized documents collection
- `MONGODB_DATABASE`: MongoDB database name

### Frontend Configuration

The frontend automatically connects to the backend API. No additional configuration needed.

### UI Parameters

The application provides a parameter panel where you can adjust:

- **Model**: Choose between different OpenAI models (GPT-4, GPT-3.5, etc.)
- **Temperature**: Control randomness in responses (0.0 - 2.0)
- **Top K Documents**: Number of documents to retrieve for RAG (1-20)
- **Max Tokens**: Maximum length of generated response
- **Frequency Penalty**: Reduce repetition (-2.0 to 2.0)
- **Presence Penalty**: Encourage new topics (-2.0 to 2.0)

## Troubleshooting

### Common Issues

1. **MongoDB Connection Error**
   - Verify your MongoDB URI and credentials
   - Ensure your IP is whitelisted in Atlas
   - Check if the database and collection exist

2. **OpenAI API Error**
   - Verify your OpenAI API key
   - Check your API usage limits
   - Ensure you have access to the required models

3. **Vector Search Not Working**
   - Verify your vector search index is created
   - Check that documents have embeddings
   - Ensure the index name matches your configuration

4. **Port Already in Use**
   - Change the PORT environment variable
   - Kill existing processes on the port

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

MIT License - see LICENSE file for details.
