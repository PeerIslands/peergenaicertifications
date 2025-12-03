"""
Configuration settings for the RAG service using python-decouple.
"""
from decouple import config


class Settings:
    """Application settings loaded from environment variables using python-decouple."""
    
    # OpenAI Configuration
    openai_api_key = config('OPENAI_API_KEY', default=None)
    
    # MongoDB Configuration
    mongodb_uri = config('MONGODB_URI', default='mongodb://localhost:27017')
    mongodb_database = config('MONGODB_DATABASE', default='rag_database')
    mongodb_collection = config('MONGODB_COLLECTION', default='documents')
    
    # Document Processing Configuration
    # Note: chunk_size and chunk_overlap are used by LangChain only
    # LlamaIndex uses Sentence Window which splits by sentences, not chunks
    chunk_size = config('CHUNK_SIZE', default=1000, cast=int)
    chunk_overlap = config('CHUNK_OVERLAP', default=200, cast=int)
    
    # Sentence Window Retrieval Configuration (LlamaIndex only)
    # Controls how many sentences before/after each match to include as context
    sentence_window_size = config('SENTENCE_WINDOW_SIZE', default=3, cast=int)
    
    # Model Configuration - Using your .env file values
    embedding_model = config('OPENAI_EMBEDDING_MODEL', default='text-embedding-ada-002')
    llm_model = config('OPENAI_LLM_MODEL', default='gpt-3.5-turbo')
    temperature = config('TEMPERATURE', default=0.7, cast=float)
    max_tokens = config('MAX_TOKENS', default=1000, cast=int)
    
    # Vector Search Configuration
    vector_index_name = config('VECTOR_INDEX_NAME', default='vector_index')
    similarity_threshold = config('SIMILARITY_THRESHOLD', default=0.7, cast=float)
    top_k_results = config('TOP_K_RESULTS', default=5, cast=int)


# Global settings instance
settings = Settings()

# Note: Configuration logging removed for production readiness
# Settings are loaded silently to avoid exposing configuration in logs