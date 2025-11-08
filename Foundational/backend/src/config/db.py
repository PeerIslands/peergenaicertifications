
import dotenv
import os
from langchain_community.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from src.config.llm import get_embedding_model

dotenv.load_dotenv()

if not os.environ["MONGODB_URI"]:
    raise ValueError("MONGODB_URI environment variable is required")

if not os.environ["MONGODB_DB_NAME"]:
    raise ValueError("MONGODB_DB_NAME environment variable is required")

if not os.environ["MONGODB_VECTOR_COLLECTION_NAME"]:
    raise ValueError("MONGODB_VECTOR_COLLECTION_NAME environment variable is required")

# MongoDB Atlas connection string
MONGODB_URI = os.getenv("MONGODB_URI")
DB_NAME = os.getenv("MONGODB_DB_NAME")
COLLECTION_NAME = os.getenv("MONGODB_VECTOR_COLLECTION_NAME")

# Connect to MongoDB
client = MongoClient(MONGODB_URI,tls=True,
                             tlsAllowInvalidCertificates=True)
collection = client[DB_NAME][COLLECTION_NAME]


# Initialize LangChain MongoDB vector store
vector_store = MongoDBAtlasVectorSearch(
    collection=collection,
    embedding=get_embedding_model(),
    index_name="vector_index"
)

retriever = vector_store.as_retriever(
   # search_type = "similarity",
   search_type="mmr",  # Changed to Maximal Marginal Relevance
   search_kwargs = { "k": 5 }
)

def get_vector_store() -> MongoDBAtlasVectorSearch:
    """Get the initialized MongoDB vector store."""
    return vector_store

def get_mongo_client() -> MongoClient:
    """Get the MongoDB client."""
    return client

def get_mongo_collection(collection_name: str):
    """Get the MongoDB collection."""
    return client[DB_NAME][collection_name]

def get_retriever():
    """Get the LangChain retriever."""
    return retriever

def clear_vector_store():
    """Clear all documents from the vector store."""
    collection.delete_many({})