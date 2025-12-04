# qa_chain.py
import os
import tempfile
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fix OpenMP conflict on macOS when using FAISS (configurable via env)
os.environ["KMP_DUPLICATE_LIB_OK"] = os.getenv("KMP_DUPLICATE_LIB_OK", "TRUE")

from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableLambda

PROMPT_TEMPLATE = """Answer the question based ONLY on the context provided below.

IMPORTANT RULES:
1. Your answer MUST be exactly 1-2 sentences. Be concise and direct.
2. If the context does not contain information to answer the question, respond with: "The answer to this question is not found in the provided context."
3. Do NOT make up or hallucinate any information. Only use what is explicitly stated in the context.
4. Do NOT mention "based on the context" or similar phrases in your answer. Just provide the answer directly.

Context: {context}

Question: {question}

Answer (1-2 sentences only):
"""


def _format_docs(docs):
    """Join LangChain documents into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def handle_user_query(chain, question: str) -> str:
    """Invoke the chain with the provided question."""
    return chain.invoke({"question": question})


def create_qa_chain(pdf_file) -> Optional[object]:
    """Create the QA chain from an uploaded PDF file."""
    tmp_path = None
    try:
        # Save uploaded file to a temporary path
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.read())
            tmp_path = tmp_file.name

        # Load PDF pages (each page is treated as a chunk)
        loader = PyPDFLoader(tmp_path)
        pages = loader.load_and_split()

        # Build and return the QA chain
        return _build_chain(pages)
    finally:
        # Clean up temporary file
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.unlink(tmp_path)
            except OSError:
                # Best-effort cleanup
                pass


def _build_chain(pages):
    """Create the runnable chain once documents are available."""
    # Read model/config from environment
    llm_model_name = os.getenv("OLLAMA_MODEL", "llama3.1")
    embedding_model_name = os.getenv("EMBEDDING_MODEL", "znbang/bge:small-en-v1.5-f32")
    # retriever_k = int(os.getenv("RETRIEVER_K", "4"))

    # LLM and embeddings from Ollama
    llm = OllamaLLM(model=llm_model_name)
    embeddings = OllamaEmbeddings(model=embedding_model_name)

    # Build FAISS vector store from page documents
    store = FAISS.from_documents(pages, embedding=embeddings)

    # Configure retriever (how many similar chunks to fetch)
    retriever = store.as_retriever()

    prompt = PromptTemplate.from_template(PROMPT_TEMPLATE)

    # Runnable graph:
    # question -> retriever -> context -> prompt -> LLM -> string output
    chain = (
        {
            "context": RunnableLambda(lambda x: x["question"]) | retriever | _format_docs,
            "question": RunnableLambda(lambda x: x["question"]),
        }
        | prompt
        | llm
        | StrOutputParser()
    )
    return chain
