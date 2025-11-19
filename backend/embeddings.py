import os
from typing import List
from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_core.documents import Document

def build_vectorstore_from_pdfs(pdf_paths: List[str], embedding_model: str = None):
    # ... (Embedder and Text Splitter setup remains the same)

    all_raw_documents = []
    for p in pdf_paths:
        if not os.path.exists(p):
            print(f"[embeddings] WARNING: file not found: {p}")
            continue

        # Use load() instead of load_and_split() to get full pages/raw text
        loader = PyPDFLoader(p)
        all_raw_documents.extend(loader.load())

    if not all_raw_documents:
        raise ValueError("No documents found/loaded.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    docs = text_splitter.split_documents(all_raw_documents)
    # The splitting process will correctly maintain the original 'source' metadata

    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vect = InMemoryVectorStore.from_documents(documents=docs, embedding=embeddings)
    return vect