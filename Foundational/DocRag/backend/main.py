from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import shutil

from rag_service import RAGService

# Load environment variables
load_dotenv()

app = FastAPI(title="RAG PDF Query API")

# CORS middleware to allow React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG service
rag_service = RAGService()

# Ensure pdfs directory exists
PDF_DIR = "pdfs"
os.makedirs(PDF_DIR, exist_ok=True)


class QueryRequest(BaseModel):
    query: str
    top_k: Optional[int] = 3


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]


class IngestResponse(BaseModel):
    message: str
    files_processed: int


@app.get("/")
async def root():
    return {"message": "RAG PDF Query API is running"}


@app.post("/api/ingest", response_model=IngestResponse)
async def ingest_pdfs(files: List[UploadFile] = File(...)):
    """
    Upload and ingest PDF files into the vector store
    """
    try:
        saved_files = []
        
        # Save uploaded files
        for file in files:
            if not file.filename.endswith('.pdf'):
                raise HTTPException(status_code=400, detail=f"File {file.filename} is not a PDF")
            
            file_path = os.path.join(PDF_DIR, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            saved_files.append(file_path)
        
        # Ingest into RAG system
        rag_service.ingest_documents(saved_files)
        
        return IngestResponse(
            message="PDFs ingested successfully",
            files_processed=len(saved_files)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the ingested documents using RAG
    """
    try:
        if not rag_service.is_initialized():
            raise HTTPException(
                status_code=400, 
                detail="No documents have been ingested yet. Please upload PDFs first."
            )
        
        result = rag_service.query(request.query, top_k=request.top_k)
        
        return QueryResponse(
            answer=result["answer"],
            sources=result["sources"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/status")
async def get_status():
    """
    Get the status of the RAG system
    """
    return {
        "initialized": rag_service.is_initialized(),
        "documents_count": rag_service.get_document_count()
    }


@app.delete("/api/reset")
async def reset_system():
    """
    Reset the RAG system and clear all documents
    """
    try:
        rag_service.reset()
        return {"message": "System reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

