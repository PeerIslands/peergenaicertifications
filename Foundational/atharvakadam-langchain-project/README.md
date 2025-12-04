## LangChain PDF QA Assistant

This project builds a local, privacy-friendly assistant that can chat with any uploaded PDF. The Streamlit single-page app handles the UX while LangChain orchestrates PDF ingestion, FAISS retrieval, and Ollama-powered generation.

### Backend Architecture

![System Architecture](docs/architecture.heic)

1. **UI Layer (`src/ui`)**
   - `app.py` renders the Streamlit SPA, handles uploads, chat rendering, and communicates with the service layer.
   - `html_templates.py` centralizes the chat theming.
2. **Service Layer (`src/services/qa_chain.py`)**
   - Accepts an uploaded PDF, uses `PyPDFLoader` to chunk it, embeds chunks via `OllamaEmbeddings` (`znbang/bge:small-en-v1.5-f32`), and stores them in an in-memory FAISS index.
   - Builds a LangChain Runnable pipeline that:
     - Converts the latest user question into retrieval queries.
     - Formats retrieved docs via `_format_docs`.
     - Fills a guarded prompt that forces 1–2 sentence grounded answers.
     - Invokes `OllamaLLM` (`llama3.1`).
3. **State Layer (`src/state/session_state.py`)**
   - Wraps Streamlit session state (current chain, chat history, dedupe logic, input-clearing behaviour) so UI code stays lean and testable.

> 💡 Place the provided architecture image at `docs/architecture.png` so the diagram renders in this README.

### Tech Stack

| Layer          | Tools / Libraries                                   | Notes                                                     |
|----------------|-----------------------------------------------------|-----------------------------------------------------------|
| UI             | Streamlit                                           | Simple SPA, custom chat components                        |
| Orchestration  | LangChain Core/Runnables                            | Deterministic pipeline composition                        |
| LLM / Embeds   | Ollama (`llama3.1` for answers, `znbang/bge` embeds) | Runs locally; pull models via `ollama pull <model>`       |
| Retrieval      | FAISS (in-memory), PyPDFLoader                      | No on-disk index; built per upload                        |
| Testing        | Pytest                                              | `tests/` covers services and session helpers              |

### Running the App Locally

1. **Prerequisites**
   - Python 3.9 (see `.python-version`)
   - [Ollama](https://ollama.com/) running locally (`ollama serve`)
   - Models: `ollama pull llama3.1` and `ollama pull znbang/bge:small-en-v1.5-f32`

2. **Install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Start the Streamlit app**
   ```bash
   streamlit run app.py
   ```

4. **Use the app**
   - Upload a PDF via the sidebar.
   - Click **Process PDF** (builds the FAISS index).
   - Ask questions in the chat input; answers are grounded, 1–2 sentence summaries.

### Running Tests

From the project root (or inside `tests/`):

```bash
pytest
```

`tests/conftest.py` ensures the `src/` package is importable, so the suite works without extra environment tweaks.

### Project Structure

```
langchain_project/
├── app.py                # Entry point (streamlit run app.py)
├── requirements.txt
├── src/
│   ├── services/
│   │   └── qa_chain.py   # PDF ingestion + LangChain pipeline
│   ├── state/
│   │   └── session_state.py
│   └── ui/
│       ├── app.py
│       └── html_templates.py
└── tests/
    ├── conftest.py
    ├── test_qa_chain.py
    └── test_session_state.py
```