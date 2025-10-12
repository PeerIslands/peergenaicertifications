from __future__ import annotations

import shutil
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from .config import settings
from .rag_service import ingest_pdfs, list_sources, delete_source, query_documents, RagError


app = FastAPI(title="ChatWithDoc RAG")

static_dir = Path(__file__).parent / "static"
templates_dir = Path(__file__).parent / "templates"

app.mount("/static", StaticFiles(directory=static_dir), name="static")


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=1)
    k: int = Field(4, ge=1, le=20)


class QueryResponse(BaseModel):
    answer: str
    sources: List[str]


@app.get("/", response_class=HTMLResponse)
def index_page() -> HTMLResponse:
    index_path = templates_dir / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail="UI not found")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))


@app.post("/api/upload")
async def upload_pdfs(files: List[UploadFile] = File(...)):
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    saved_paths: List[str] = []
    for f in files:
        if not f.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Only PDF files are supported: {f.filename}")
        dest = Path(settings.upload_dir) / f.filename
        with dest.open("wb") as out:
            shutil.copyfileobj(f.file, out)
        saved_paths.append(str(dest))
    try:
        results = ingest_pdfs(saved_paths)
    except RagError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"ingested": [r.__dict__ for r in results]}


@app.get("/api/pdfs")
def get_pdfs():
    try:
        sources = list_sources()
    except RagError as e:
        raise HTTPException(status_code=500, detail=str(e))
    return {"sources": sources}


@app.delete("/api/pdfs/{filename}")
def delete_pdf(filename: str):
    try:
        count = delete_source(filename)
    except RagError as e:
        raise HTTPException(status_code=500, detail=str(e))
    # Also delete physical file if present
    path = Path(settings.upload_dir) / filename
    if path.exists():
        try:
            path.unlink()
        except Exception:
            pass
    return {"deleted_chunks": count}


@app.post("/api/query", response_model=QueryResponse)
def query_api(req: QueryRequest):
    try:
        answer, docs = query_documents(req.question, k=req.k)
    except RagError as e:
        raise HTTPException(status_code=400, detail=str(e))
    sources = []
    for d in docs:
        src = d.metadata.get("source", "unknown")
        if src not in sources:
            sources.append(src)
    return QueryResponse(answer=answer, sources=sources)


