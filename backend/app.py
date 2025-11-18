import os
import re
from flask import Flask, request, jsonify, send_from_directory
from sentence_transformers import SentenceTransformer
import chromadb

# /**
#  * Application settings and constants.
#  * @constant {string} PERSIST_DIR - Directory for Chroma persistent DB.
#  * @constant {string} COLLECTION_NAME - Name of the collection to load/use.
#  * @constant {string} OLLAMA_MODEL - Local Ollama model identifier.
#  */
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "chroma_db")
COLLECTION_NAME = "peer-ai-table"
OLLAMA_MODEL = "gemma3:1b"

# /**
#  * Initialize a persistent Chroma client.
#  * This will create or open the SQLite/flat-file store at PERSIST_DIR.
#  *
#  * @type {chromadb.PersistentClient}
#  */
client = chromadb.PersistentClient(path=PERSIST_DIR)

# /**
#  * Try to load an existing collection; if it doesn't exist, create it.
#  *
#  * @throws {chromadb.errors.NotFoundError} when collection missing (handled here).
#  * @type {chromadb.api.models.Collection.Collection}
#  */
try:
    collection = client.get_collection(COLLECTION_NAME)
    print(f"Loaded collection: {COLLECTION_NAME}")
except chromadb.errors.NotFoundError:
    print(f"Collection '{COLLECTION_NAME}' not found. Creating new collection.")
    collection = client.create_collection(COLLECTION_NAME)

# /**
#  * Sentence-transformers model used for query embeddings.
#  * Instantiated once and reused for efficiency.
#  *
#  * @type {SentenceTransformer}
#  * @model all-MiniLM-L6-v2
#  */
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# /**
#  * Create Flask app instance.
#  * @type {Flask}
#  */
app = Flask(__name__)


# /**
#  * Clean text by removing non-ASCII characters and compressing whitespace.
#  *
#  * @param {string} s - Input string to clean.
#  * @returns {string} cleaned ASCII-only string.
#  */
def clean_text_ascii(s: str) -> str:
    s2 = re.sub(r"[^\x00-\x7F]+", " ", s)
    s2 = re.sub(r"\s+", " ", s2).strip()
    return s2


# /**
#  * Robust extractor for various possible shapes of response returned by ollama.chat().
#  * Tries dict keys, attributes, lists, and falls back to str(resp).
#  *
#  * @param {*} resp - Raw response object returned from Ollama client.
#  * @returns {string} Extracted text (empty string if nothing useful found).
#  */
def extract_ollama_answer(resp) -> str:
    # 1) dict-like response
    if isinstance(resp, dict):
        if "choices" in resp and len(resp["choices"]) > 0:
            try:
                return resp["choices"][0].get("message", {}).get("content", "") or str(resp["choices"][0])
            except Exception:
                return str(resp)
        if "result" in resp and len(resp["result"]) > 0:
            first = resp["result"][0]
            if isinstance(first, dict):
                return first.get("content") or first.get("text") or str(first)
            else:
                return str(first)
        if "text" in resp:
            return resp.get("text") or ""
        if "content" in resp:
            return resp.get("content") or ""
        return ""

    # 2) object-like responses (attributes)
    msg_attr = getattr(resp, "message", None)
    if msg_attr is not None:
        if isinstance(msg_attr, (list, tuple)):
            first = msg_attr[0]
            return getattr(first, "content", None) or getattr(first, "text", None) or str(first)
        else:
            return getattr(msg_attr, "content", None) or getattr(msg_attr, "text", None) or str(msg_attr)

    res_attr = getattr(resp, "result", None)
    if res_attr:
        if isinstance(res_attr, (list, tuple)):
            first = res_attr[0]
            return getattr(first, "content", None) or getattr(first, "text", None) or str(first)
        else:
            return getattr(res_attr, "content", None) or getattr(res_attr, "text", None) or str(res_attr)

    choices_attr = getattr(resp, "choices", None)
    if choices_attr and len(choices_attr) > 0:
        first = choices_attr[0]
        msg = getattr(first, "message", None) or first
        return getattr(msg, "content", None) or getattr(msg, "text", None) or str(msg)

    # final fallback
    try:
        return str(resp)
    except Exception:
        return ""


# /**
#  * Serve the frontend index.html from the ../frontend directory.
#  *
#  * @route GET /
#  * @returns {Response} index.html content
#  */
@app.route("/")
def index():
    return send_from_directory("../frontend", "index.html")


# /**
#  * Main query endpoint.
#  *
#  * POST JSON body: { "q": "<user query>" }
#  *
#  * Flow:
#  *  1. Validate input.
#  *  2. Compute embedding for query.
#  *  3. Query Chroma for nearest document chunks.
#  *  4. Truncate and clean top chunks into a compact context.
#  *  5. Build a concise prompt and call Ollama local model.
#  *  6. Extract answer robustly and return JSON: { answer, retrieved }.
#  *
#  * @route POST /query
#  * @returns {JSON} { answer: string, retrieved: string[] }
#  */
@app.route("/query", methods=["POST"])
def query():
    data = request.json or {}
    q = data.get("q", "").strip()
    if not q:
        return jsonify({"error": "Missing 'q' in JSON body"}), 400

    # 1) retrieve nearest chunks
    q_emb = embed_model.encode([q])[0]
    results = collection.query(query_embeddings=[q_emb], n_results=4)
    docs = results.get("documents", [[]])[0]

    # 2) prepare truncated, cleaned context (top 3 chunks, ~80 words each)
    top_chunks = []
    for chunk in docs[:3]:
        chunk_clean = clean_text_ascii(chunk)
        words = chunk_clean.split()
        truncated = " ".join(words[:80])
        top_chunks.append(truncated)
    context = "\n\n".join(top_chunks)

    # 3) build concise prompt for the local Ollama model
    prompt = f"""You are an AI assistant. Based on the context below, answer the question concisely.
Context:
{context}

Question: {q}

Respond with only the answer (one or two short sentences)."""

    # 4) call Ollama and extract answer
    answer = ""
    try:
        from ollama import Client as OllamaClient
        ollama = OllamaClient()
        resp = ollama.chat(model=OLLAMA_MODEL, messages=[{"role": "user", "content": prompt}])
        print("DEBUG: raw ollama resp type:", type(resp))
        print("DEBUG: raw ollama repr (first 800 chars):", repr(resp)[:800])
        answer = extract_ollama_answer(resp).strip()
    except Exception as e:
        print("Ollama call exception:", e)
        answer = ""

    # 5) fallback if Ollama didn't return usable text
    if not answer:
        answer = "Ollama returned empty or unexpected response."

    return jsonify({
        "answer": answer,
        "retrieved": top_chunks
    })


# /**
#  * Run the Flask development server when executed as a script.
#  *
#  * @example python app.py
#  */
if __name__ == "__main__":
    print("Starting Flask app...")
    app.run(host="0.0.0.0", port=5000, debug=True)
