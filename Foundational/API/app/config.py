import os
from pymongo import MongoClient
import openai

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "rag_project"
COLLECTION_NAME = "documents"

# Mongo connection
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

# OpenAI API Key
openai.api_key = os.getenv("OPENAI_API_KEY")
