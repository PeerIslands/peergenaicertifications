import os
import io
import zipfile
from pathlib import Path

import streamlit as st
from PyPDF2 import PdfReader
from dotenv import load_dotenv

# LangChain imports
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# FREE EMBEDDINGS (local, no API cost)
from langchain_community.embeddings import HuggingFaceEmbeddings

# FREE LLM from GROQ
from langchain_groq import ChatGroq


# ----------------------------------------------
# Load environment variables
# ----------------------------------------------
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    st.error("GROQ_API_KEY missing in .env file.")
    st.stop()


# ----------------------------------------------
# Initialize Embeddings & LLM (FREE)
# ----------------------------------------------

# FIXED: force CPU to avoid PyTorch meta-tensor crash on Windows
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2",
    model_kwargs={"device": "cpu"}    # REQUIRED FIX
)

# FIXED: Updated Groq model (old model decommissioned)
llm = ChatGroq(
    model="llama-3.3-70b-versatile",   # UPDATED MODEL
    api_key=GROQ_API_KEY,
    temperature=0
)

# Local ChromaDB folder
CHROMA_PATH = "chroma_db"


# ----------------------------------------------
# Extract PDF text
# ----------------------------------------------
def extract_pdf_text(pdf_bytes):
    reader = PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        text += page.extract_text() or ""
    return text


# ----------------------------------------------
# Extract ZIP (code repo)
# ----------------------------------------------
def extract_zip_files(zip_bytes):
    z = zipfile.ZipFile(io.BytesIO(zip_bytes))
    all_text = ""

    allowed_exts = [".py", ".js", ".txt", ".md", ".json", ".yaml", ".yml"]

    for file in z.namelist():
        ext = Path(file).suffix.lower()
        if ext in allowed_exts:
            try:
                content = z.read(file).decode("utf-8", errors="replace")
                all_text += f"\n### FILE: {file}\n{content}\n"
            except:
                pass

    return all_text


# ----------------------------------------------
# Chunking
# ----------------------------------------------
def chunk_text(text, chunk_size=1000, overlap=200):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=overlap,
    )
    return splitter.split_text(text)


# ----------------------------------------------
# Build Chroma Vector DB
# ----------------------------------------------
def build_vector_store(chunks):
    docs = [Document(page_content=c) for c in chunks]

    vectordb = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=CHROMA_PATH,
    )

    vectordb.persist()
    return vectordb


# ----------------------------------------------
# Main Streamlit UI
# ----------------------------------------------
st.title("RAG App — LangChain + ChromaDB + Groq + HF Embeddings")
st.markdown("Upload PDF or ZIP (code repo) and ask questions")

uploaded = st.file_uploader("Upload PDF or ZIP", type=["pdf", "zip"])
chunk_size = st.number_input("Chunk size", 500, 5000, value=1000)
overlap = st.number_input("Overlap", 0, 500, value=200)

process = st.button("Process Document", key="process_button")

if process and uploaded:
    st.info("Extracting text...")

    if uploaded.name.endswith(".pdf"):
        raw_text = extract_pdf_text(uploaded.read())
    else:
        raw_text = extract_zip_files(uploaded.read())

    st.success("Extraction complete!")

    st.info("Chunking...")
    chunks = chunk_text(raw_text, chunk_size, overlap)
    st.write(f"Total chunks: {len(chunks)}")

    st.info("Creating vector store...")
    vectordb = build_vector_store(chunks)
    st.success("Document indexed into ChromaDB!")


# ----------------------------------------------
# Load existing DB
# ----------------------------------------------
if Path(CHROMA_PATH).exists():
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=CHROMA_PATH,
    )
    retriever = vectordb.as_retriever()

    qa_prompt = ChatPromptTemplate.from_messages([
        (
            "system",
            "You are an assistant that answers using ONLY the provided context.\n"
            "If the answer is not found, say: 'I don't know from the document'.\n\n"
            "Context:\n{context}\n"
        ),
        ("human", "{question}")
    ])

    rag_chain = (
        {
            "context": retriever | (lambda docs: "\n\n".join([d.page_content for d in docs])),
            "question": RunnablePassthrough(),
        }
        | qa_prompt
        | llm
        | StrOutputParser()
    )
else:
    vectordb = None


st.markdown("---")

# ----------------------------------------------
# Chat interface
# ----------------------------------------------
st.header("Ask Questions")
question = st.text_input("Your question:")

ask = st.button("Ask", key="ask_button")

if ask:
    if vectordb is None:
        st.error("Please upload and process a document first.")
    else:
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []

        answer = rag_chain.invoke(question)

        st.write("### Answer:")
        st.write(answer)

        st.session_state["chat_history"].append((question, answer))
