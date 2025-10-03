from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.config.settings import Settings
from src.rag.system import initialize_rag_system, list_available_pdfs


class QueryRequest(BaseModel):
    query: str


class QueryResponse(BaseModel):
    result: str
    sources: Optional[list[Dict[str, Any]]] = None


def create_app() -> FastAPI:
    app = FastAPI(title="RAG API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    settings = Settings()
    # Lazy-initialize to avoid hard failure if PDFs are not yet present
    app.state.qa_chain = None
    app.state.startup_error = None

    @app.get("/health")
    def health() -> Dict[str, Any]:
        return {
            "status": "ok" if getattr(app.state, "startup_error", None) is None else "degraded",
            "error": getattr(app.state, "startup_error", None),
            "pdfs": list_available_pdfs(settings),
        }

    @app.get("/")
    def root() -> RedirectResponse:
        return RedirectResponse(url="/docs", status_code=307)

    @app.post("/reload")
    def reload() -> Dict[str, Any]:
        try:
            app.state.qa_chain = initialize_rag_system(settings)
            app.state.startup_error = None
            return {"status": "ok"}
        except Exception as exc:
            app.state.qa_chain = None
            app.state.startup_error = str(exc)
            raise HTTPException(status_code=503, detail=f"Reload error: {exc}")

    @app.get("/query")
    def query_get() -> Dict[str, Any]:
        return {
            "message": "Use POST /query with JSON body { 'query': 'your question' }"
        }

    @app.post("/query", response_model=QueryResponse)
    def query(request: QueryRequest) -> QueryResponse:
        if not request.query or len(request.query.strip()) == 0:
            raise HTTPException(status_code=400, detail="Query must be a non-empty string")
        try:
            # Initialize on first use if needed
            if app.state.qa_chain is None:
                app.state.qa_chain = initialize_rag_system(settings)
                app.state.startup_error = None
            result = app.state.qa_chain.invoke(request.query)
            sources: list[Dict[str, Any]] = []
            for doc in result.get("source_documents", []) or []:
                sources.append({
                    "source": doc.metadata.get("source", "N/A"),
                    "page": doc.metadata.get("page", "N/A"),
                })
            return QueryResponse(result=result.get("result", ""), sources=sources)
        except Exception as exc:
            app.state.startup_error = str(exc)
            raise HTTPException(status_code=500, detail=str(exc)) from exc

    return app


app = create_app()


