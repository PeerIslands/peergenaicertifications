from fastapi import FastAPI
from dotenv import load_dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

from routes import upload, chat,news

app = FastAPI(title="LLM + RAG with OpenAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["http://localhost:5500"] for your UI port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(chat.router, prefix="/chat", tags=["Chat"])
app.include_router(news.router, prefix="/news", tags=["News"])

@app.get("/")
def root():
    return {"message": "✅ RAG API with OpenAI is running"}
