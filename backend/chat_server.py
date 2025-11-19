import os
import json
from dotenv import load_dotenv
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
from langchain_core.prompts import ChatPromptTemplate
from embeddings import build_vectorstore_from_pdfs

load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_FOLDER = os.path.join(BASE_DIR, "../frontend", "static")

app = Flask(
    __name__,
    static_folder=FRONTEND_FOLDER,
    static_url_path=""
)

CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise RuntimeError("Set GROQ_API_KEY in .env")

backend_dir = os.path.dirname(__file__)
PDF_FOLDER = os.path.join(backend_dir, "pdfs")

pdf_files = [
    os.path.join(PDF_FOLDER, f)
    for f in os.listdir(PDF_FOLDER)
    if f.lower().endswith(".pdf")
]

print("[server] PDF files detected:", pdf_files)

print("Building vector store...")
vectorstore = build_vectorstore_from_pdfs(pdf_files)
print("[server] Vector store ready. Indexed chunks:", len(vectorstore._docs) if hasattr(vectorstore, "_docs") else "unknown")

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    temperature=0.2
)

memories = {}  # session_id -> list[BaseMessage]

def get_memory(session_id: str):
    return memories.setdefault(session_id, [])

prompt_template = ChatPromptTemplate.from_template("""
You are an AI Career Advisor. But try to answer in 2-3 lines and be specific.
Use the retrieved context below when it's helpful.

Context:
{context}

Conversation history (most recent last):
{chat_history}

User: {question}
Assistant:""")

def build_context_from_retrieved(query: str, k: int = 3):
    docs = vectorstore.similarity_search(query, k=k)
    # docs typically consist of Document objects with .page_content and .metadata
    ctx_parts = []
    for i, d in enumerate(docs):
        src = d.metadata.get("source", "unknown")
        ctx_parts.append(f"[Doc {i+1} | source: {src}]\n{d.page_content}\n")
    return "\n---\n".join(ctx_parts)

# API -
@app.route("/")
def index():
    return send_from_directory(FRONTEND_FOLDER, "index.html")

@app.route("/api/chat", methods=["POST"])
def chat():
    payload = request.get_json() or {}
    message = payload.get("message", "").strip()
    session_id = payload.get("session_id", "default")  # simple session id

    if not message:
        return jsonify({"error": "empty message"}), 400

    # Retrieve context via vectorstore
    context = build_context_from_retrieved(message, k=3)

    # Load conversation history
    hist_messages = get_memory(session_id)
    # create a single flattened history string for the prompt
    chat_history_str = "\n".join(
        [f"{'User' if isinstance(m, HumanMessage) else 'Assistant'}: {m.content}" for m in hist_messages]
    )

    # Final prompt
    prompt_value = prompt_template.format_prompt(
        context=context,
        chat_history=chat_history_str,
        question=message
    )


    llm_result = llm.generate_prompt([prompt_value])

    generations = getattr(llm_result, "generations", None)
    if not generations:
        # fallback: try llm.generate(...)
        return jsonify({"error": "LLM returned no generations"}), 500

    answer = generations[0][0].text if generations and generations[0] and generations[0][0] else ""

    # Save to memory (append human message + ai message)
    hist_messages.append(HumanMessage(content=message))
    hist_messages.append(AIMessage(content=answer))
    memories[session_id] = hist_messages

    # Return response and chat_history in simple format
    # Convert memory messages to a serializable list
    chat_history_serializable = [
        {"role": "user" if isinstance(m, HumanMessage) else "assistant", "content": m.content}
        for m in hist_messages
    ]

    return jsonify({
        "answer": answer,
        "chat_history": chat_history_serializable,
        "context_used": context
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
