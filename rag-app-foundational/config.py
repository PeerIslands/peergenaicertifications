"""
Configuration for the RAG application with Azure OpenAI.
Optimized for Replit deployment.
"""
import os

# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT = "https://app-tx-peer.openai.azure.com/"
AZURE_OPENAI_API_VERSION = "2024-06-01"
AZURE_OPENAI_EMBEDDING_DEPLOYMENT = "text-embedding-ada-002"
AZURE_OPENAI_CHAT_DEPLOYMENT = "gpt-4o"

# API Key - can be set via environment or UI
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY", "")

# Vector store settings
VECTOR_STORE_PATH = "vector_store"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# PDF directory
PDF_DIR = "pdfs"

# Replit optimized - no local models
USE_LOCAL_MODELS = False
