# LangChain Integration Guide

This project now includes powerful LangChain integration for enhanced RAG (Retrieval-Augmented Generation) capabilities.

## 🚀 What's New with LangChain

### Enhanced Features
- **Advanced Text Splitting**: Uses LangChain's `RecursiveCharacterTextSplitter` for intelligent document chunking
- **Vector Store**: In-memory vector store for efficient similarity search
- **Runnable Chains**: Structured LLM workflows with proper input/output handling
- **Better Embeddings**: OpenAI embeddings with fallback to hash-based method
- **Enhanced Prompts**: Structured prompt templates for consistent responses

## 📦 Installed Packages

- `langchain` - Core LangChain framework
- `@langchain/openai` - OpenAI integration (ChatGPT + Embeddings)
- `@langchain/community` - Community integrations and vector stores
- `@langchain/core` - Core abstractions and interfaces

## 🔧 Configuration

### Environment Variables
```bash
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

### LangChain Components
The integration automatically configures:
- **Chat Model**: `openai/gpt-oss-20b:free` via OpenRouter
- **Embeddings**: `text-embedding-ada-002` via OpenRouter
- **Text Splitter**: Recursive character-based splitting with 1000 char chunks and 200 char overlap

## 🔧 Integration Points

LangChain components are integrated directly into the existing services:

### 1. Enhanced OpenAI Service (`openaiService.ts`)
- **Prompt Templates**: Structured RAG prompts using `PromptTemplate`
- **Runnable Chains**: LLM workflows with `RunnableSequence`
- **Output Parsers**: Consistent response formatting with `StringOutputParser`

### 2. Enhanced RAG Service (`ragService.ts`)
- **Text Splitting**: Advanced document chunking with `RecursiveCharacterTextSplitter`
- **Better Chunking**: Intelligent text segmentation with overlap and semantic coherence

### 3. Available LangChain Components
- **ChatOpenAI**: Enhanced LLM integration
- **OpenAIEmbeddings**: Embedding generation (available for future use)
- **Text Splitters**: Advanced document processing
- **Prompt Templates**: Structured prompt management
- **Runnable Sequences**: Workflow orchestration

## 🧪 Testing

Run the test script to verify integrated LangChain functionality:

```bash
# Make sure you have your API key set
export OPENROUTER_API_KEY="your_key_here"

# Run the test
node test-langchain.mjs
```

The test script will:
1. Test text splitting with RecursiveCharacterTextSplitter
2. Test OpenAI embeddings (available for future use)
3. Test LLM responses with ChatOpenAI
4. Test RAG prompt templates and chains
5. Test RunnableSequence workflows

## 🔍 How It Works

### 1. Document Processing
```
PDF Upload → Text Extraction → LangChain Text Splitting → Embedding Generation → Vector Store Storage
```

### 2. RAG Search
```
User Query → Query Embedding → Vector Similarity Search → Context Assembly → LLM Response Generation
```

### 3. Text Splitting Strategy
- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Separators**: `["\n\n", "\n", ". ", "! ", "? ", " ", ""]`
- **Keep Separators**: Yes (for better context)

## 🎯 Benefits Over Previous Implementation

1. **Better Text Chunking**: LangChain's recursive splitter maintains semantic coherence
2. **Efficient Vector Search**: In-memory vector store with similarity search
3. **Structured Chains**: Proper input/output handling with RunnableSequence
4. **Fallback Support**: Graceful degradation when OpenAI services are unavailable
5. **Metadata Tracking**: Better document and chunk management
6. **Performance Metrics**: Search time and relevance scoring

## 🚨 Error Handling

The system includes comprehensive error handling:
- **API Failures**: Automatic fallback to hash-based embeddings
- **Missing Documents**: Clear error messages when no content is available
- **Invalid Queries**: Validation and helpful error responses
- **Processing Errors**: Detailed logging for debugging

## 🔮 Future Enhancements

Potential improvements to consider:
- **Persistent Vector Store**: Database-backed storage for production use
- **Hybrid Search**: Combine semantic and keyword search
- **Document Metadata**: Enhanced metadata extraction and storage
- **Batch Processing**: Process multiple documents simultaneously
- **Caching**: Response caching for repeated queries

## 📖 Additional Resources

- [LangChain Documentation](https://js.langchain.com/)
- [OpenAI API Reference](https://platform.openai.com/docs)
- [Vector Store Concepts](https://js.langchain.com/docs/modules/data_connection/vectorstores/)

## 🤝 Contributing

When adding new LangChain features:
1. Follow the existing service pattern
2. Include proper error handling
3. Add comprehensive tests
4. Update this documentation
5. Consider backward compatibility

---

**Note**: This integration maintains compatibility with the existing RAG service while providing enhanced capabilities through LangChain.
