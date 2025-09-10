# MongoDB Vector Store Setup

This application now uses MongoDB as a vector store for document storage and retrieval. Follow these steps to set up MongoDB for your PDF RAG application.

## Prerequisites

1. **MongoDB Atlas** (recommended) or **Local MongoDB installation**
2. **Node.js** with npm/yarn

## Setup Instructions

### Option 1: MongoDB Atlas (Recommended)

1. **Create a MongoDB Atlas account** at [mongodb.com/atlas](https://mongodb.com/atlas)
2. **Create a new cluster** (free tier available)
3. **Create a database user** with read/write permissions
4. **Get your connection string** from the Atlas dashboard
5. **Set environment variables**:

```bash
# Create .env file in the project root
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DATABASE=pdf_rag
OPENAI_API_KEY=your_openai_api_key_here
PORT=8080
```

### Option 2: Local MongoDB

1. **Install MongoDB locally**:
   ```bash
   # macOS with Homebrew
   brew install mongodb-community
   
   # Start MongoDB service
   brew services start mongodb-community
   ```

2. **Set environment variables**:
```bash
# Create .env file in the project root
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pdf_rag
OPENAI_API_KEY=your_openai_api_key_here
PORT=8080
```

## Vector Search Index Setup

The application will automatically create the necessary vector search index when it starts. However, for MongoDB Atlas, you may need to manually create the index:

1. **Go to your MongoDB Atlas dashboard**
2. **Navigate to your cluster → Search → Create Index**
3. **Create a Vector Search Index** with these settings:
   - **Index Name**: `vector_index`
   - **Collection**: `document_chunks`
   - **Vector Field**: `embedding`
   - **Dimensions**: `1536` (OpenAI embedding dimensions)
   - **Similarity**: `cosine`

## Installation

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Start the application**:
   ```bash
   npm run dev
   ```

## Features

### Vector Search Capabilities
- **Semantic similarity search** using OpenAI embeddings
- **Cosine similarity** for accurate document retrieval
- **Configurable similarity threshold** (default: 0.7)
- **Automatic fallback** to text search if vector search fails

### Document Processing
- **PDF text extraction** and chunking
- **Automatic embedding generation** for each chunk
- **Metadata storage** including document names and chunk types
- **Status tracking** (uploading, processing, ready, error)

### Performance Optimizations
- **MongoDB indexes** for fast queries
- **Vector search aggregation** for efficient similarity search
- **Connection pooling** for better performance
- **Error handling** with graceful fallbacks

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | Database name | `pdf_rag` |
| `OPENAI_API_KEY` | OpenAI API key for embeddings | Required |
| `PORT` | Server port | `8080` |

### Vector Search Configuration

You can modify the vector search settings in `shared/mongodb-schema.ts`:

```typescript
export const VECTOR_SEARCH_CONFIG = {
  VECTOR_FIELD: 'embedding',
  SIMILARITY_THRESHOLD: 0.7,  // Adjust for more/less strict matching
  MAX_RESULTS: 10,            // Maximum results per search
  INDEX_NAME: 'vector_index',
} as const;
```

## Troubleshooting

### Common Issues

1. **Connection Error**: Check your MongoDB URI and ensure the database is accessible
2. **Vector Search Not Working**: Verify the vector search index is created in MongoDB Atlas
3. **Slow Performance**: Consider upgrading your MongoDB Atlas cluster or optimizing your queries

### Debug Mode

Enable debug logging by setting:
```bash
NODE_ENV=development
```

## Migration from Memory Storage

If you're migrating from the previous memory storage:

1. **Export existing data** (if needed)
2. **Update your environment variables**
3. **Restart the application** - it will automatically use MongoDB
4. **Re-upload your documents** to populate the vector store

## Support

For issues related to:
- **MongoDB setup**: Check the [MongoDB documentation](https://docs.mongodb.com/)
- **Vector search**: See [MongoDB Atlas Search documentation](https://docs.atlas.mongodb.com/atlas-search/)
- **Application issues**: Check the application logs and error messages
