from fastapi import APIRouter, HTTPException
from typing import List
from services.file_processor import FileProcessor
from services.vector_store import VectorStore
from models.pdf_metadata import DocumentResponse, PDFMetadata
from datetime import datetime

router = APIRouter()

# Initialize services
file_processor = FileProcessor()
vector_store = VectorStore()

@router.post("/reload", response_model=DocumentResponse)
async def reload_files():
    """Reload and process all files from the files directory"""
    try:
        # Clear existing chunks
        await vector_store.clear_all_chunks()
        
        # Process all files from files directory
        processed_files = file_processor.process_all_files()
        
        if not processed_files:
            raise HTTPException(status_code=400, detail="No valid PDF files found in files directory")
        
        # Store chunks in vector database
        total_chunks = await vector_store.store_chunks(processed_files)
        
        # Prepare response
        processed_files_list = []
        for file_data in processed_files:
            metadata = PDFMetadata(
                file_name=file_data["file_name"],
                file_size=file_data["file_size"],
                processed_time=datetime.now(),
                chunk_count=file_data["chunk_count"]
            )
            processed_files_list.append(metadata)
        
        return DocumentResponse(
            message=f"Successfully reloaded {len(processed_files)} files with {total_chunks} chunks",
            processed_files=processed_files_list,
            total_chunks=total_chunks
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reloading files: {str(e)}")

@router.get("/status")
async def get_document_status():
    """Get current status of loaded documents"""
    try:
        chunk_count = await vector_store.get_chunk_count()
        doc_count = await vector_store.get_document_count()
        
        return {
            "total_documents": doc_count,
            "total_chunks": chunk_count,
            "status": "ready" if chunk_count > 0 else "no_documents"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting status: {str(e)}")
