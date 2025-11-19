import streamlit as st
import os
import requests
import json
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Load API key from environment (.env) for security. Falls back to None if not set.
from dotenv import load_dotenv
load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")


GEMINI_EMBED_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent?key={API_KEY}"
GEMINI_CHAT_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={API_KEY}"

template = """
You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Use three sentences maximum and keep the answer concise.
Question: {question} 
Context: {context} 
Answer:
"""

pdfs_directory = 'chat-with-pdf/pdfs/'
os.makedirs(pdfs_directory, exist_ok=True)

# In-memory store for vectors
documents_store = []  # each item: {'content': ..., 'embedding': ...}

# ---- Gemini Embedding ----
# Replace your previous get_gemini_embedding with this
def get_gemini_embedding(text):
    GEMINI_EMBED_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-embedding-001:embedContent"
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": API_KEY,
    }

    # correct request body shape per Gemini docs: content.parts[].text
    body = {
        "model": "models/gemini-embedding-001",
        "content": {
            "parts": [
                {"text": text}
            ]
        }
    }

    try:
        response = requests.post(GEMINI_EMBED_URL, headers=headers, json=body, timeout=20)
        result = response.json()
    except Exception as e:
        st.warning(f"Embedding request failed: {e}")
        return None

    # Typical response: result["embedding"] (object) or result["embeddings"] (list)
    # Try the most common shapes first, then fall back to searching for a float list
    emb = None
    if isinstance(result, dict):
        # common: result["embedding"]["value"]
        emb_obj = result.get("embedding") or (result.get("embeddings") and result["embeddings"][0])
        if isinstance(emb_obj, dict) and "value" in emb_obj:
            emb = emb_obj["value"]
        elif isinstance(emb_obj, list):
            emb = emb_obj
        # some versions: result["embeddings"] -> list of dicts with "embedding" key
        elif "embeddings" in result and isinstance(result["embeddings"], list) and result["embeddings"]:
            first = result["embeddings"][0]
            if isinstance(first, dict):
                if "embedding" in first and isinstance(first["embedding"], dict) and "value" in first["embedding"]:
                    emb = first["embedding"]["value"]
                elif "embedding" in first and isinstance(first["embedding"], list):
                    emb = first["embedding"]

    # fallback: find any list-of-floats nested in the response
    if emb is None:
        def find_list_of_floats(obj):
            if isinstance(obj, list) and obj and all(isinstance(x, (int, float)) for x in obj):
                return obj
            if isinstance(obj, dict):
                for v in obj.values():
                    found = find_list_of_floats(v)
                    if found:
                        return found
            if isinstance(obj, list):
                for item in obj:
                    found = find_list_of_floats(item)
                    if found:
                        return found
            return None
        emb = find_list_of_floats(result)

    if emb is None:
        st.warning("Couldn't parse embedding from Gemini response. See logs for raw response.")
        st.write(result)
        return None

    try:
        return np.array(emb, dtype=np.float32).reshape(-1)
    except Exception as e:
        st.warning(f"Failed converting embedding to numpy array: {e}")
        return None
# ---------------------------

# ---- Gemini Answer Generator ----
def answer_question_with_gemini(question, context):
    prompt = template.format(question=question, context=context)

    # DEBUG: show final prompt (console + UI)
    final_prompt = prompt
    print("[DEBUG] Final prompt to Gemini Chat API:\n" + final_prompt)
    try:
        st.write("**DEBUG: Final prompt to Gemini Chat API**")
        st.code(final_prompt)
    except Exception:
        pass

    headers = {"Content-Type": "application/json"}
    body = {
        "contents": [
            {
                "parts": [
                    {"text": prompt}
                ]
            }
        ]
    }

    try:
        response = requests.post(GEMINI_CHAT_URL, headers=headers, json=body, timeout=20)
        result = response.json()
    except Exception as e:
        print(f"[DEBUG] Chat request failed: {e}")
        return f"Sorry, chat request failed: {e}"

    # try a few common result shapes
    try:
        # typical: result["candidates"][0]["content"]["parts"][0]["text"]
        if "candidates" in result and isinstance(result["candidates"], list) and result["candidates"]:
            cand = result["candidates"][0]
            if isinstance(cand, dict) and "content" in cand:
                cont = cand["content"]
                if isinstance(cont, dict) and "parts" in cont and cont["parts"]:
                    return cont["parts"][0].get("text", "")
        # alternative: result["output"][0]["content"][0]["text"]
        if "output" in result and isinstance(result["output"], list) and result["output"]:
            out0 = result["output"][0]
            if isinstance(out0, dict) and "content" in out0 and out0["content"]:
                c0 = out0["content"][0]
                if isinstance(c0, dict) and "text" in c0:
                    return c0["text"]
    except Exception:
        pass

    # fallback: return stringified result (small)
    raw = json.dumps(result)[:1000]
    print("[DEBUG] Gemini Chat raw response (truncated):", raw)
    try:
        st.write("**DEBUG: Gemini Chat raw response (truncated)**")
        st.write(raw)
    except Exception:
        pass
    return raw

# ---- Text Handling ----
def upload_pdf(file):
    with open(os.path.join(pdfs_directory, file.name), "wb") as f:
        f.write(file.getbuffer())

def load_pdf(file_path):
    loader = PDFPlumberLoader(file_path)
    return loader.load()

def split_text(documents):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        add_start_index=True
    )
    return text_splitter.split_documents(documents)

# ---- Indexing ----
def index_documents(chunks):
    indexed = 0
    # For debugging, print each chunk and its embedding summary as it's indexed
    for i, chunk in enumerate(chunks, start=1):
        text = chunk.page_content
        embedding = get_gemini_embedding(text)
        if embedding is not None:
            # Console debug: show chunk number, length and a short excerpt
            try:
                excerpt = text.replace("\n", " ")[:300]
            except Exception:
                excerpt = text[:300]
            print(f"[DEBUG] Chunk #{i} (len={len(text)}): {excerpt}...")

            # Console debug: embedding length and first few values
            try:
                emb_list = embedding.tolist() if hasattr(embedding, 'tolist') else list(embedding)
                print(f"[DEBUG] Embedding #{i}: len={len(emb_list)} first_10={emb_list[:10]}")
            except Exception as e:
                print(f"[DEBUG] Failed to print embedding #{i}: {e}")

            # Also attempt to show in Streamlit UI for convenience
            try:
                st.write(f"**DEBUG: Chunk #{i}**")
                st.write(excerpt + "...")
                st.write(f"**DEBUG: Embedding #{i} (len={len(emb_list)}) - first 10:**")
                st.write(emb_list[:10])
            except Exception:
                # If Streamlit isn't running (e.g., running unit tests), ignore UI logging
                pass

            documents_store.append({"content": text, "embedding": embedding})
            indexed += 1
    return indexed

# ---- Retrieval ----
def retrieve_relevant_docs(query, top_k=3):
    query_embedding = get_gemini_embedding(query)
    if query_embedding is None or not documents_store:
        return []

    similarities = []
    for doc in documents_store:
        # ensure both embeddings are 1D numpy arrays
        doc_emb = np.array(doc["embedding"], dtype=np.float32).reshape(1, -1)
        q_emb = query_embedding.reshape(1, -1)
        # sklearn cosine_similarity expects 2D arrays
        sim = cosine_similarity(q_emb, doc_emb)[0][0]
        similarities.append((sim, doc["content"]))

    similarities.sort(reverse=True, key=lambda x: x[0])
    return [doc for _, doc in similarities[:top_k]]

# ---- Streamlit App ----
uploaded_file = st.file_uploader("Upload PDF", type="pdf")

if uploaded_file:
    upload_pdf(uploaded_file)
    docs = load_pdf(os.path.join(pdfs_directory, uploaded_file.name))
    chunks = split_text(docs)
    st.info(f"Split into {len(chunks)} chunks.")
    indexed_count = index_documents(chunks)
    st.success(f"PDF processed and indexed. Indexed chunks: {indexed_count}. Total stored docs: {len(documents_store)}")

    question = st.chat_input("Ask a question about the PDF")
    if question:
        st.chat_message("user").write(question)
        relevant_contexts = retrieve_relevant_docs(question)
        if not relevant_contexts:
            st.chat_message("assistant").write("Sorry — I couldn't find relevant passages (or embeddings failed).")
        else:
            context = "\n\n".join(relevant_contexts)
            answer = answer_question_with_gemini(question, context)
            st.chat_message("assistant").write(answer)
