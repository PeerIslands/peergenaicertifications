# AskPDF Server Architecture

## Overview

The AskPDF server has been refactored into a modular, service-oriented architecture that separates concerns and makes the codebase more maintainable and testable.

## Architecture Diagram

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Routes        │    │   Services      │    │   LangChain     │
│   (routes.ts)   │───▶│   (services/)   │───▶│   Components    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   MongoDB       │
                       │   Atlas         │
                       └─────────────────┘
```

## Service Architecture

### 1. ConfigService (`services/configService.ts`)
- **Purpose**: Centralized configuration management
- **Responsibilities**:
  - Load and validate environment variables
  - Provide configuration to other services
  - Mask sensitive data in logs
- **Key Features**:
  - Singleton pattern for global access
  - Configuration validation
  - Safe configuration exposure

### 2. LangChainService (`services/langchainService.ts`)
- **Purpose**: All LangChain LLM operations
- **Responsibilities**:
  - Chat model initialization and management
  - Query expansion using LLM
  - RAG response generation
  - Direct LLM responses
- **Key Features**:
  - Dynamic parameter configuration
  - Error handling and fallbacks
  - Model abstraction

### 3. VectorService (`services/vectorService.ts`)
- **Purpose**: Vector operations and document retrieval
- **Responsibilities**:
  - MongoDB Atlas Vector Search integration
  - BM25 keyword search implementation
  - Hybrid search coordination
  - Document indexing and retrieval
- **Key Features**:
  - Reciprocal Rank Fusion (RRF) algorithm
  - Parallel search execution
  - Document statistics

### 4. RAGOrchestrator (`services/ragOrchestrator.ts`)
- **Purpose**: Coordinate all RAG operations
- **Responsibilities**:
  - Orchestrate search and generation
  - Context assembly
  - Response formatting
  - Service coordination
- **Key Features**:
  - Query expansion integration
  - Hybrid search management
  - Context optimization

## File Structure

```
server/
├── services/
│   ├── index.ts              # Service exports
│   ├── configService.ts      # Configuration management
│   ├── langchainService.ts   # LangChain operations
│   ├── vectorService.ts      # Vector operations
│   └── ragOrchestrator.ts    # RAG coordination
├── routes.ts                 # API endpoints
├── ragServiceNew.ts          # Backward compatibility
├── ragService.ts             # Legacy service (deprecated)
└── ARCHITECTURE.md           # This file
```

## API Endpoints

### Core RAG Endpoints
- `POST /api/chat` - Main RAG chat endpoint
- `GET /api/chat/history/:userId` - Chat history
- `GET /api/chat/history/entry/:id` - Specific chat entry

### Search Endpoints
- `POST /api/search/semantic` - Semantic search only
- `POST /api/search/keyword` - Keyword search only
- `POST /api/expand-query` - Query expansion

### LLM Endpoints
- `POST /api/llm/direct` - Direct LLM response (no RAG)

### System Endpoints
- `GET /api/health` - Health check
- `GET /api/config` - System configuration

## Configuration

### Environment Variables

#### Required
- `OPENAI_API_KEY` - OpenAI API key
- `MONGODB_URI` - MongoDB connection string

#### Optional
- `OPENAI_BASE_URL` - OpenAI API base URL
- `OPENAI_API_VERSION` - API version
- `CHAT_MODEL` - Chat model name
- `EMBEDDING_MODEL` - Embedding model name
- `ENABLE_QUERY_EXPANSION` - Enable query expansion
- `MONGODB_DATABASE` - Database name
- `MONGODB_COLLECTION` - Collection name

## Usage Examples

### Using the New Architecture

```typescript
import { RAGOrchestrator, ConfigService } from './services';

// Initialize services
const configService = ConfigService.getInstance();
const ragOrchestrator = new RAGOrchestrator(configService.getConfig());
await ragOrchestrator.initialize();

// Perform RAG search
const response = await ragOrchestrator.search("What is machine learning?", 5);

// Perform semantic search only
const semanticResults = await ragOrchestrator.semanticSearch("AI", 3);

// Expand query
const expandedQuery = await ragOrchestrator.expandQuery("ML");
```

### Backward Compatibility

```typescript
import { getRAGService } from './ragServiceNew';

// Legacy interface still works
const ragService = getRAGService();
await ragService.initialize();
const response = await ragService.search("query", 5);
```

## Benefits of New Architecture

### 1. **Separation of Concerns**
- Each service has a single responsibility
- Easier to test and maintain
- Clear interfaces between components

### 2. **Modularity**
- Services can be used independently
- Easy to swap implementations
- Better code reusability

### 3. **Configuration Management**
- Centralized configuration
- Environment validation
- Safe configuration exposure

### 4. **Error Handling**
- Service-specific error handling
- Graceful degradation
- Better error reporting

### 5. **Extensibility**
- Easy to add new services
- Plugin-like architecture
- Future-proof design

## Migration Guide

### From Old to New Architecture

1. **Update imports**:
   ```typescript
   // Old
   import { getRAGService } from './ragService';
   
   // New
   import { RAGOrchestrator, ConfigService } from './services';
   ```

2. **Initialize services**:
   ```typescript
   // Old
   const ragService = getRAGService();
   await ragService.initialize();
   
   // New
   const configService = ConfigService.getInstance();
   const ragOrchestrator = new RAGOrchestrator(configService.getConfig());
   await ragOrchestrator.initialize();
   ```

3. **Use new methods**:
   ```typescript
   // Old
   const response = await ragService.search(query, k, params);
   
   // New (same interface)
   const response = await ragOrchestrator.search(query, k, params);
   
   // New (additional methods)
   const semanticResults = await ragOrchestrator.semanticSearch(query, k);
   const expandedQuery = await ragOrchestrator.expandQuery(query);
   ```

## Testing

Each service can be tested independently:

```typescript
// Test configuration service
const configService = ConfigService.getInstance();
expect(configService.validateConfig().isValid).toBe(true);

// Test vector service
const vectorService = new VectorService(config);
await vectorService.initialize();
const results = await vectorService.performSemanticSearch("test", 5);

// Test LangChain service
const langchainService = new LangChainService(config);
const response = await langchainService.generateResponse("test");
```

## Future Enhancements

1. **Caching Layer**: Add Redis caching for frequent queries
2. **Monitoring**: Add metrics and logging
3. **Rate Limiting**: Implement API rate limiting
4. **Authentication**: Add user authentication
5. **Multi-tenancy**: Support multiple document collections
6. **Streaming**: Add streaming responses
7. **Webhooks**: Add webhook support for events
