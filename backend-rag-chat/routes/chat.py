from fastapi import APIRouter, HTTPException
from models.chat_request import ChatRequest, ChatResponse
from services.vector_store import VectorStore
from services.rag_pipeline import RAGPipeline
from services.conversation_memory import conversation_memory
import uuid
from datetime import datetime

router = APIRouter()

# Initialize services
vector_store = VectorStore()
rag_pipeline = RAGPipeline(vector_store)

@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Process chat query and return RAG response"""
    try:
        # Generate session ID if not provided
        session_id = request.session_id or str(uuid.uuid4())
        
        # Check if we have any documents
        chunk_count = await vector_store.get_chunk_count()
        if chunk_count == 0:
            return ChatResponse(
                response="Please ensure documents are loaded from the files directory before asking questions.",
                sources=[],
                session_id=session_id
            )
        
        # Add user message to conversation memory
        conversation_memory.add_message(session_id, "user", request.query)
        
        # Generate RAG response
        result = await rag_pipeline.generate_response(request.query, session_id)
        
        # Add assistant response to conversation memory
        conversation_memory.add_message(session_id, "assistant", result["response"], result["sources"])
        
        return ChatResponse(
            response=result["response"],
            sources=result["sources"],
            session_id=session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")

@router.delete("/reset")
async def reset_documents():
    """Clear all stored document embeddings"""
    try:
        deleted_count = await vector_store.clear_all_chunks()
        return {
            "message": f"Successfully cleared {deleted_count} document chunks",
            "deleted_count": deleted_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing documents: {str(e)}")

@router.delete("/clear-memory/{session_id}")
async def clear_conversation_memory(session_id: str):
    """Clear conversation memory for a specific session"""
    try:
        conversation_memory.clear_conversation(session_id)
        return {
            "message": f"Successfully cleared conversation memory for session {session_id}",
            "session_id": session_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing conversation memory: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        chunk_count = await vector_store.get_chunk_count()
        return {
            "status": "healthy",
            "total_chunks": chunk_count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }
