from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import uvicorn
from src.services.process_file_service import ProcessFileService
from src.services.session_service import SessionsService
from src.services.chat_service import ChatService
from src.config.db import clear_vector_store

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="ChatPDF API",
    description="A FastAPI service for PDF chat using LangChain",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
file_service = ProcessFileService()
session_service = SessionsService()
chat_service = ChatService()

# Pydantic models
class ChatMessage(BaseModel):
    message: str
    session_id: Optional[str] = None

class ChatResponse(BaseModel):
    response: str
    session_id: str

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
async def root():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        message="ChatPDF API is running"
    )

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Detailed health check"""
    return HealthResponse(
        status="healthy",
        message="All services are operational"
    )

@app.post("/upload", response_model=dict)
async def upload_file(file: UploadFile = File(...)):
    """Upload and process a PDF file"""
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed")
        
        # Check file size
        max_size = int(os.getenv("MAX_FILE_SIZE", 10485760))  # 10MB default
        content = await file.read()
        if len(content) > max_size:
            raise HTTPException(status_code=400, detail="File too large")
        
        # Process the file with LangChain
        session_id = await file_service.process_document(file.filename, content)
        
        return {
            "message": "File uploaded and processed successfully",
            "session_id": session_id,
            "filename": file.filename
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/files/{file_id}")
async def delete_files(file_id: str):
    """Upload and process a PDF file"""
    try:
        # Validate file_id
        if not file_id:
            raise HTTPException(status_code=400, detail="File ID is required")

        # Check file size
        status = await file_service.delete_file(file_id)

        #Temporarily clear vector store on file deletion
        clear_vector_store()


        return status

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/chat/{session_id}", response_model=ChatResponse)
async def chat_with_document(chat_message: ChatMessage, session_id: str):
    """Chat with the uploaded document"""
    try:
        if not chat_message.message.strip():
            raise HTTPException(status_code=400, detail="Message cannot be empty")
        
        response = await chat_service.chat(
            message=chat_message.message,
            session_id=session_id
        )
        
        return ChatResponse(
            response=response,
            session_id=session_id
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/messages/{session_id}", response_model=List[dict])
async def get_messages(session_id: str):
    """Retrieve chat history for a session"""
    try:
        if not session_id.strip():
            raise HTTPException(status_code=400, detail="Session ID cannot be empty")

        messages = await chat_service.get_messages(session_id)
        return messages
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/session")
async def create_sessions():
    """Get all active chat sessions"""
    try:
        session_id = await session_service.create_session()
        return session_id
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/sessions")
async def get_sessions():
    """Get all active chat sessions"""
    try:
        sessions = await session_service.create_session()
        return {"sessions": sessions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/session/{session_id}")
async def delete_session(session_id: str):
    """Delete a specific chat session"""
    try:
        success = await session_service.delete_session(session_id)
        if success:
            return {"message": "Session deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail="Session not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files")
async def get_files():
    """Get all active chat sessions"""
    try:
        files = await file_service.get_files()
        return files
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    debug = os.getenv("DEBUG", "True").lower() == "true"
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=debug
    )
