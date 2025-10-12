from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import json
from pathlib import Path
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

from rag_pipeline import RAGPipeline
app = FastAPI(title="RAG Document Chat API")

import logging
import sys

# Configure root logger
logging.basicConfig(
    level=logging.INFO,  # Or DEBUG for even more detail
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

rag_pipeline = RAGPipeline()

class ChatRequest(BaseModel):
    message: str
    model: str = "openai"
    session_id: str = "default"

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float

@app.get("/")
async def root():
    return {"message": "RAG Document Chat API", "status": "running"}

@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    try:
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        file_path = upload_dir / file.filename
        
        content = await file.read()
        with open(file_path, "wb") as f:
            f.write(content)
        
        result = await rag_pipeline.process_document(str(file_path), file.filename)
        
        return {
            "status": "success",
            "filename": file.filename,
            "chunks_created": result["chunks_created"],
            "message": f"Successfully processed {file.filename}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat")
async def chat(request: ChatRequest):
    try:
        if not rag_pipeline.has_documents():
            raise HTTPException(
                status_code=400, 
                detail="No documents uploaded. Please upload documents first."
            )
        
        response = await rag_pipeline.chat(
            message=request.message,
            model=request.model,
            session_id=request.session_id
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reset")
async def reset_session(session_id: str = "default"):
    try:
        rag_pipeline.reset_session(session_id)
        return {"status": "success", "message": "Session reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents():
    try:
        docs = rag_pipeline.list_documents()
        return {"documents": docs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "azure_openai_api_key": "set" if os.getenv("AZURE_OPENAI_API_KEY") else "missing",
        "azure_openai_endpoint": "set" if os.getenv("AZURE_OPENAI_ENDPOINT") else "missing",
        "azure_chat_deployment": os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT", "not set"),
        "azure_embedding_deployment": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "not set"),
        "openai_api_key": "set" if os.getenv("OPENAI_API_KEY") else "missing",
        "google_api_key": "set" if os.getenv("GOOGLE_API_KEY") else "missing",
        "anthropic_api_key": "set" if os.getenv("ANTHROPIC_API_KEY") else "missing",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
