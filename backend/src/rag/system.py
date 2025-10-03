import os
import asyncio
from typing import Optional

from dotenv import load_dotenv, find_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_ollama import ChatOllama, OllamaEmbeddings
from langchain.chains import RetrievalQA

from src.config.settings import Settings, ensure_directories_exist


load_dotenv(find_dotenv())


def _get_event_loop() -> asyncio.AbstractEventLoop:
    try:
        return asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return loop


def initialize_rag_system(settings: Optional[Settings] = None) -> RetrievalQA:
    settings = settings or Settings()
    ensure_directories_exist(settings)

    _get_event_loop()  # ensure loop exists

    pdf_primary = settings.pdf_dir
    pdf_fallback = os.path.join(settings.project_root, "pdfs")
    for d in (pdf_primary, pdf_fallback):
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)

    # Load PDFs from primary and fallback
    documents = []
    for pdf_dir in (pdf_primary, pdf_fallback):
        if os.path.isdir(pdf_dir):
            for file in os.listdir(pdf_dir):
                if file.lower().endswith(".pdf"):
                    file_path = os.path.join(pdf_dir, file)
                    loader = PyPDFLoader(file_path)
                    documents.extend(loader.load())

    if not documents:
        raise ValueError(
            f"No PDF documents found in {pdf_primary} or {pdf_fallback}. Please add some PDFs."
        )

    # Split
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    if not splits:
        raise ValueError("Text splitting resulted in an empty list of chunks.")

    # Embeddings
    embeddings = OllamaEmbeddings(model=settings.ollama_embed_model, base_url=settings.ollama_base_url)

    # Vector store
    vectorstore = Chroma.from_documents(documents=splits, embedding=embeddings)

    # LLM
    llm = ChatOllama(model=settings.ollama_llm_model, temperature=0, base_url=settings.ollama_base_url)

    # RAG chain
    qa_chain = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(),
        return_source_documents=True,
    )
    return qa_chain


def list_available_pdfs(settings: Optional[Settings] = None) -> list[str]:
    settings = settings or Settings()
    pdf_primary = settings.pdf_dir
    pdf_fallback = os.path.join(settings.project_root, "pdfs")
    found: list[str] = []
    for pdf_dir in (pdf_primary, pdf_fallback):
        if os.path.isdir(pdf_dir):
            for file in os.listdir(pdf_dir):
                if file.lower().endswith(".pdf"):
                    found.append(os.path.join(pdf_dir, file))
    return found


