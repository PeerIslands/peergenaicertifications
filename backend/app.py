import os
import re
import logging
from flask import Flask, request, jsonify, send_from_directory
from sentence_transformers import SentenceTransformer
import chromadb
from ollama import Client as OllamaClient

BASE_DIR = os.path.dirname(__file__)
FRONTEND_DIR = os.path.join(BASE_DIR, "../frontend")
PERSIST_DIR = os.path.join(BASE_DIR, "chroma_db")
COLLECTION_NAME = "AI-table"
OLLAMA_MODEL = "gemma3:1b"

os.environ["OTEL_SDK_DISABLED"] = "true"

logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

logger.info("Initializing ChromaDB persistent client...")
client = chromadb.PersistentClient(path=PERSIST_DIR)

try:
    collection = client.get_collection(COLLECTION_NAME)
    logger.info(f"Loaded collection: {COLLECTION_NAME}")
except ValueError:
    logger.info("Collection missing — creating...")
    collection = client.create_collection(name=COLLECTION_NAME)

logger.info("Loading embedding model...")
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

logger.info("Connecting to Ollama...")
ollama_client = OllamaClient(host="http://localhost:11434")

def clean_text(s: str) -> str:
    s = re.sub(r"[^\x00-\x7F]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()

def build_prompt(question, context_docs):
    ctx = "\n\n".join(context_docs)
    return f"""
You are an AI assistant. Use ONLY the following context.
Question: {question}

Context:
{ctx}

Answer:
""".strip()

app = Flask(__name__, static_folder=FRONTEND_DIR, static_url_path="")

# Serve UI
@app.route("/")
def serve_index():
    return send_from_directory(FRONTEND_DIR, "index.html")

@app.route("/<path:filename>")
def serve_static_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)

# RAG Endpoint
@app.route("/query", methods=["POST"])
def rag_query():
    data = request.get_json()
    if not data or "question" not in data:
        return jsonify({"error": "Missing 'question'"}), 400

    question = clean_text(data["question"])
    logger.info(f"QUERY: {question}")

    q_embed = embed_model.encode([question])[0].tolist()
    results = collection.query(query_embeddings=[q_embed], n_results=3)
    docs = results.get("documents", [[]])[0]

    prompt = build_prompt(question, docs)

    try:
        resp = ollama_client.generate(model=OLLAMA_MODEL, prompt=prompt)
        answer = resp.get("response", "").strip()
    except Exception as e:
        return jsonify({"error": "LLM error", "details": str(e)}), 500

    return jsonify({
        "question": question,
        "context_used": docs,
        "answer": answer
    })

if __name__ == "__main__":
    logger.info("Starting on http://0.0.0.0:5000 ...")
    app.run(host="0.0.0.0", port=5000, debug=True)

