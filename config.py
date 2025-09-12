import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configuration settings
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "rag_database")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "documents")

# Model settings
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
