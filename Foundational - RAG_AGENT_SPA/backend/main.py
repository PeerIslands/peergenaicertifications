from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import uvicorn
from typing import List, Optional
import logging

from rag_system import RAGSystem
from document_processor import DocumentProcessor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="RAG Document QA System", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG system
rag_system = None
document_processor = DocumentProcessor()


class QueryRequest(BaseModel):
    query: str
    max_results: Optional[int] = 5


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]
    confidence: float


class UploadResponse(BaseModel):
    message: str
    documents_processed: int


@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    try:
        rag_system = RAGSystem()
        logger.info("RAG system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG system: {e}")
        raise


@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "RAG Document QA System is running!"}


@app.post("/upload", response_model=UploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Upload and process PDF documents"""
    try:
        if not rag_system:
            raise HTTPException(status_code=500,
                                detail="RAG system not initialized")

        processed_count = 0
        for file in files:
            if file.filename.endswith('.pdf'):
                # Save uploaded file temporarily
                file_path = f"temp_{file.filename}"
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # Process the document
                documents = document_processor.process_pdf(file_path)
                rag_system.add_documents(documents)

                # Clean up temporary file
                os.remove(file_path)
                processed_count += 1

        return UploadResponse(
            message=f"Successfully processed {processed_count} documents",
            documents_processed=processed_count)

    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query the RAG system with a question"""
    try:
        if not rag_system:
            raise HTTPException(status_code=500,
                                detail="RAG system not initialized")

        if not rag_system.has_documents():
            raise HTTPException(
                status_code=400,
                detail=
                "No documents uploaded. Please upload PDF documents first.")

        # Get response from RAG system
        response = rag_system.query(request.query,
                                    max_results=request.max_results)

        return QueryResponse(answer=response["answer"],
                             sources=response["sources"],
                             confidence=response["confidence"])

    except Exception as e:
        logger.error(f"Error querying documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/documents/count")
async def get_document_count():
    """Get the number of documents in the system"""
    if not rag_system:
        raise HTTPException(status_code=500,
                            detail="RAG system not initialized")

    return {"document_count": rag_system.get_document_count()}


@app.delete("/documents")
async def clear_documents():
    """Clear all documents from the system"""
    try:
        if not rag_system:
            raise HTTPException(status_code=500,
                                detail="RAG system not initialized")

        rag_system.clear_documents()
        return {"message": "All documents cleared successfully"}

    except Exception as e:
        logger.error(f"Error clearing documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
