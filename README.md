RAG + LangChain + Ollama — Local AI Chat Application

A simple fully local RAG chat application that runs 100% offline.
It loads your PDFs, converts them into embeddings, stores them in ChromaDB, and answers your questions using a local LLM via Ollama — no API keys required.

1. Install Python

Install Python (3.10+) from:
https://www.python.org/downloads/

Make sure to select:

Add Python to PATH

Install pip

2. Install Ollama

Download Ollama:
https://ollama.com/download

Verify installation:

ollama --version


Pull the LLM (example):

ollama pull gemma3:1b
ollama run gemma3:1b

3. Setup Python Environment

Move into backend folder:

cd backend


Create and activate virtual environment:

macOS / Linux
python3 -m venv venv
source venv/bin/activate

Windows
python -m venv venv
venv\Scripts\activate

4. Install Dependencies (Updated)

Install via:

pip install -r requirements.txt


Updated requirements.txt:

flask
langchain==0.1.12
chromadb==0.5.0
sentence-transformers==2.7.0
pypdf==4.2.0
ollama==0.6.1
huggingface-hub==0.22.2
transformers==4.40.1
numpy==1.26.4
torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

5. Ingest PDFs Into ChromaDB

Store PDFs in:

backend/pdfs/


Run ingestion:

python ingest.py

6. Start the Backend Server

Run the Flask server:

python app.py


Open:

http://127.0.0.1:5000/

7. Use the Chat UI

Ask any question

App embeds your query

Retrieves context from your PDFs

Ollama model generates an answer based on that context

UI Screenshot
