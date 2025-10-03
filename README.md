## React + FastAPI Production-Ready Setup

### Prerequisites
- Python 3.10+
- Node 18+
- Ollama running locally with models defined in `.env` or defaults

### Backend (FastAPI)
1. Create a venv and install deps:
   - `python -m venv .venv && . .venv/Scripts/Activate.ps1`
   - `pip install -r requirements.txt`
2. Run dev server:
   - `./scripts/run_backend.ps1`
3. API Endpoints:
   - `GET /health` → status
   - `POST /query` → body: `{ "query": "..." }`

### Frontend (React + Vite)
1. `cd frontend`
2. `npm install`
3. Create `.env` with `VITE_API_BASE=http://127.0.0.1:8000`
4. `npm run dev`

### Tests
- `pytest`

### Project Structure
- Backend API: `src/api/main.py`
- RAG System: `src/rag/system.py`
- Frontend: `frontend/`

### Production Notes
- Enable proper CORS allowlist in `src/api/main.py`
- Run with `uvicorn` or `gunicorn` behind a reverse proxy
- Consider Dockerizing backend and frontend for deployment

