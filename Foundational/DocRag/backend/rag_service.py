import os
from typing import List, Dict
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from dotenv import load_dotenv
import openai

load_dotenv()


class RAGService:
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.document_count = 0
        
        # Initialize HuggingFace embeddings (free, local, no API key needed)
        # Using 'all-MiniLM-L6-v2' - fast, efficient, and good quality
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={'normalize_embeddings': True}
        )
        
        # Initialize Azure OpenAI client
        self.client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT") or "",
            api_version=os.getenv("AZURE_OPENAI_API_VERSION")
        )
        
        # Store deployment name for chat
        self.chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
        
        # Text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
    
    def ingest_documents(self, pdf_paths: List[str]):
        """
        Ingest PDF documents into the vector store
        """
        all_documents = []
        
        # Load and split each PDF
        for pdf_path in pdf_paths:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
            split_docs = self.text_splitter.split_documents(documents)
            all_documents.extend(split_docs)
        
        # Create or update vector store
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(all_documents, self.embeddings)
        else:
            # Add new documents to existing vector store
            new_vector_store = FAISS.from_documents(all_documents, self.embeddings)
            self.vector_store.merge_from(new_vector_store)
        
        self.document_count = len(all_documents)
        
        # Create retriever
        self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 3})
    
    def query(self, query: str, top_k: int = 3) -> Dict[str, any]:
        """
        Query the RAG system using Azure OpenAI
        """
        if self.vector_store is None:
            raise ValueError("RAG system not initialized. Please ingest documents first.")
        
        # Update retriever with top_k
        self.retriever.search_kwargs = {"k": top_k}
        
        # Retrieve relevant documents
        docs = self.retriever.invoke(query)
        
        # Format context from documents
        context = "\n\n".join([doc.page_content for doc in docs])
        
        # Create the prompt
        system_message = """You are a helpful AI assistant that answers questions based on the provided context. 
Use the following pieces of context to answer the question. 
If you don't know the answer or the context doesn't contain relevant information, just say that you don't know, don't try to make up an answer."""
        
        user_message = f"""Context:
{context}

Question: {query}

Answer: Let me help you with that based on the provided documents."""
        
        # Call Azure OpenAI API directly
        response = self.client.chat.completions.create(
            model=self.chat_deployment,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract answer
        answer = response.choices[0].message.content
        
        # Extract source information
        sources = []
        for doc in docs:
            source_info = doc.metadata.get("source", "Unknown")
            page = doc.metadata.get("page", "N/A")
            sources.append(f"{os.path.basename(source_info)} (Page {page + 1})")
        
        return {
            "answer": answer,
            "sources": list(set(sources))  # Remove duplicates
        }
    
    def is_initialized(self) -> bool:
        """
        Check if the RAG system is initialized
        """
        return self.vector_store is not None
    
    def get_document_count(self) -> int:
        """
        Get the number of document chunks in the vector store
        """
        return self.document_count
    
    def reset(self):
        """
        Reset the RAG system
        """
        self.vector_store = None
        self.retriever = None
        self.document_count = 0

