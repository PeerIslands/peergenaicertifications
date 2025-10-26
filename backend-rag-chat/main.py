from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import documents, chat
from services.vector_store import VectorStore
from services.file_processor import FileProcessor
import asyncio

app = FastAPI(
    title="RAG Chat API",
    description="Retrieval-Augmented Generation Chat API with Pre-loaded PDF Documents",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(documents.router, prefix="/api", tags=["documents"])
app.include_router(chat.router, prefix="/api", tags=["chat"])

@app.on_event("startup")
async def startup_event():
    """Initialize vector store and process files from files directory"""
    vector_store = VectorStore()
    await vector_store.create_index()
    print("Vector store initialized successfully")
    
    # Check if we already have documents loaded
    chunk_count = await vector_store.get_chunk_count()
    if chunk_count == 0:
        print("No documents found, processing files from files directory...")
        file_processor = FileProcessor()
        processed_files = file_processor.process_all_files()
        
        if processed_files:
            total_chunks = await vector_store.store_chunks(processed_files)
            print(f"Successfully processed {len(processed_files)} files with {total_chunks} chunks")
        else:
            print("No files were processed")
    else:
        print(f"Found {chunk_count} existing chunks, skipping file processing")

@app.get("/")
async def root():
    return {"message": "RAG Chat API is running", "version": "1.0.0"}

@app.get("/api/")
async def api_root():
    return {
        "message": "RAG Chat API",
        "endpoints": {
            "chat": "/api/chat",
            "reset": "/api/reset",
            "status": "/api/status",
            "health": "/api/health",
            "reload": "/api/reload"
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
