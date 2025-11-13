from fastapi import APIRouter, UploadFile, File
from services import document_reader, chunker, embedder, retriever
import tempfile
import os
from services.db import collection
import numpy as np

router = APIRouter()

@router.post("/")
async def upload_file(file: UploadFile = File(...)):
    # Save temporarily
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    # Extract text
    text = document_reader.extract_text(temp_path, file.filename)
    chunks = chunker.chunk_text(text)
    embeddings = embedder.embed_text(chunks)

    # Store in MongoDB
    docs = [
        {"filename": file.filename, "chunk": c, "embedding": e}
        for c, e in zip(chunks, embeddings)
    ]
    if docs:
        collection.insert_many(docs)

    # Update in-memory retriever
    retriever.retriever_engine.add(embeddings, chunks)

    os.remove(temp_path)
    return {"status": "success", "chunks_stored": len(chunks)}
