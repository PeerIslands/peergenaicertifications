"""
Configuration settings for the document ingestion system
"""
import os
from pathlib import Path

# Default configuration
DEFAULT_CONFIG = {
    # MongoDB settings
    'MONGODB_URI': os.getenv('MONGODB_URI', ''),
    'DATABASE_NAME': os.getenv('DATABASE_NAME', 'doc-analysis'),
    'COLLECTION_NAME': 'doc-store',
    
    # PDF processing settings
    'PDF_FOLDER': os.getenv('PDF_FOLDER', './PDF'),
    'CHUNK_SIZE': int(os.getenv('CHUNK_SIZE', '1000')),
    'CHUNK_OVERLAP': int(os.getenv('CHUNK_OVERLAP', '200')),
    'BATCH_SIZE': int(os.getenv('BATCH_SIZE', '50')),
    
    # Azure OpenAI settings
    'USE_AZURE_OPENAI': os.getenv('USE_AZURE_OPENAI', 'false').lower() == 'true',
    'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
    'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY', ''),
    'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
    'AZURE_OPENAI_DEPLOYMENT_NAME': os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME', 'gpt-4o-mini'),
    'AZURE_EMBEDDING_DEPLOYMENT_NAME': os.getenv('AZURE_EMBEDDING_DEPLOYMENT_NAME', 'text-embedding-ada-002'),
    
    # Logging settings
    'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    'LOG_FILE': os.getenv('LOG_FILE', 'ingestion.log'),
    
    # Output settings
    'STATS_FILE': os.getenv('STATS_FILE', 'ingestion_stats.json'),
    'VERBOSE': os.getenv('VERBOSE', 'false').lower() == 'true'
}

# Supported embedding models and their dimensions
EMBEDDING_MODELS = {
    'all-MiniLM-L6-v2': 384,
    'all-mpnet-base-v2': 768,
    'all-distilroberta-v1': 768,
    'paraphrase-multilingual-MiniLM-L12-v2': 384,
    'paraphrase-multilingual-mpnet-base-v2': 768
}

# File processing settings
SUPPORTED_EXTENSIONS = ['.pdf']
MAX_FILE_SIZE_MB = 100  # Maximum file size to process
MIN_CHUNK_SIZE = 50     # Minimum chunk size in characters
MAX_CHUNK_SIZE = 5000   # Maximum chunk size in characters

# Database indexes to create
DATABASE_INDEXES = [
    {'keys': [('text', 'text')], 'name': 'text_search'},
    {'keys': [('document_id', 1)], 'name': 'document_id'},
    {'keys': [('page_number', 1)], 'name': 'page_number'},
    {'keys': [('chunk_index', 1)], 'name': 'chunk_index'},
    {'keys': [('document_id', 1), ('page_number', 1)], 'name': 'document_page'},
    {'keys': [('document_id', 1), ('chunk_index', 1)], 'name': 'document_chunk'}
]

def get_config():
    """Get current configuration"""
    return DEFAULT_CONFIG.copy()

def update_config(**kwargs):
    """Update configuration with new values"""
    config = get_config()
    config.update(kwargs)
    return config

def validate_config(config):
    """Validate configuration values"""
    errors = []
    
    # Validate chunk settings
    if config['CHUNK_SIZE'] < MIN_CHUNK_SIZE:
        errors.append(f"CHUNK_SIZE must be at least {MIN_CHUNK_SIZE}")
    
    if config['CHUNK_SIZE'] > MAX_CHUNK_SIZE:
        errors.append(f"CHUNK_SIZE must be at most {MAX_CHUNK_SIZE}")
    
    if config['CHUNK_OVERLAP'] >= config['CHUNK_SIZE']:
        errors.append("CHUNK_OVERLAP must be less than CHUNK_SIZE")
    
    # Validate embedding model
    if config['EMBEDDING_MODEL'] not in EMBEDDING_MODELS:
        errors.append(f"EMBEDDING_MODEL must be one of: {list(EMBEDDING_MODELS.keys())}")
    
    # Validate paths
    pdf_folder = Path(config['PDF_FOLDER'])
    if not pdf_folder.exists():
        errors.append(f"PDF_FOLDER does not exist: {pdf_folder}")
    
    if errors:
        raise ValueError("Configuration validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    
    return True
