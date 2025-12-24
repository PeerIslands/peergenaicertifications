"""
RAG Engine - Core retrieval and generation logic using LangChain with Azure OpenAI
Simplified for Replit compatibility
"""
import os
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import config


class RAGEngine:
    """RAG Engine for document retrieval and question answering with Azure OpenAI."""
    
    def __init__(self):
        self.vector_store = None
        self.retriever = None
        self.embeddings = None
        self.llm = None
        self.api_key = config.AZURE_OPENAI_API_KEY
    
    def set_api_key(self, api_key: str) -> dict:
        """Set the Azure OpenAI API key and initialize models."""
        self.api_key = api_key
        try:
            self._initialize_models()
            # Reload vector store if it exists
            if os.path.exists(config.VECTOR_STORE_PATH):
                self.load_vector_store()
            return {"success": True, "message": "API key configured successfully"}
        except Exception as e:
            return {"success": False, "message": f"Failed to initialize: {str(e)}"}
    
    def _initialize_models(self):
        """Initialize Azure OpenAI embeddings and LLM."""
        if not self.api_key:
            print("No Azure OpenAI API key configured")
            self.embeddings = None
            self.llm = None
            return
        
        try:
            from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
            
            # Initialize Azure OpenAI Embeddings
            self.embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                azure_deployment=config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT,
                api_version=config.AZURE_OPENAI_API_VERSION,
                api_key=self.api_key
            )
            
            # Initialize Azure OpenAI Chat (GPT-4o)
            self.llm = AzureChatOpenAI(
                azure_endpoint=config.AZURE_OPENAI_ENDPOINT,
                azure_deployment=config.AZURE_OPENAI_CHAT_DEPLOYMENT,
                api_version=config.AZURE_OPENAI_API_VERSION,
                api_key=self.api_key,
                temperature=0.3
            )
            
            print("Azure OpenAI models initialized successfully")
            print(f"  - Embeddings: {config.AZURE_OPENAI_EMBEDDING_DEPLOYMENT}")
            print(f"  - Chat: {config.AZURE_OPENAI_CHAT_DEPLOYMENT}")
            
        except Exception as e:
            print(f"Error initializing Azure OpenAI: {e}")
            self.embeddings = None
            self.llm = None
            raise
    
    def is_configured(self) -> bool:
        """Check if the API key is configured and models are initialized."""
        return self.embeddings is not None and self.llm is not None
    
    def load_pdfs(self, pdf_directory: str) -> List:
        """Load all PDFs from a directory."""
        documents = []
        
        if not os.path.exists(pdf_directory):
            print(f"PDF directory not found: {pdf_directory}")
            return documents
        
        pdf_files = [f for f in os.listdir(pdf_directory) if f.endswith('.pdf')]
        print(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            pdf_path = os.path.join(pdf_directory, pdf_file)
            try:
                loader = PyPDFLoader(pdf_path)
                docs = loader.load()
                # Add source metadata
                for doc in docs:
                    doc.metadata['source_file'] = pdf_file
                documents.extend(docs)
                print(f"Loaded: {pdf_file} ({len(docs)} pages)")
            except Exception as e:
                print(f"Error loading {pdf_file}: {e}")
        
        return documents
    
    def create_vector_store(self, documents: List) -> bool:
        """Create vector store from documents."""
        if not documents:
            print("No documents to process")
            return False
        
        if not self.embeddings:
            print("Embeddings not initialized. Please set API key first.")
            return False
        
        # Split documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=["\n\n", "\n", " ", ""]
        )
        chunks = text_splitter.split_documents(documents)
        print(f"Created {len(chunks)} chunks from documents")
        
        # Create vector store
        try:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
            # Save vector store
            self.vector_store.save_local(config.VECTOR_STORE_PATH)
            print(f"Vector store saved to {config.VECTOR_STORE_PATH}")
            
            # Set up retriever
            self.retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            return True
        except Exception as e:
            print(f"Error creating vector store: {e}")
            return False
    
    def load_vector_store(self) -> bool:
        """Load existing vector store."""
        if not self.embeddings:
            print("Embeddings not initialized. Please set API key first.")
            return False
        
        try:
            if os.path.exists(config.VECTOR_STORE_PATH):
                self.vector_store = FAISS.load_local(
                    config.VECTOR_STORE_PATH,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.retriever = self.vector_store.as_retriever(
                    search_type="similarity",
                    search_kwargs={"k": 4}
                )
                print("Vector store loaded successfully")
                return True
        except Exception as e:
            print(f"Error loading vector store: {e}")
        return False
    
    def clear_vector_store(self) -> dict:
        """Clear the vector store and delete saved files."""
        import shutil
        
        try:
            # Clear in-memory store
            self.vector_store = None
            self.retriever = None
            
            # Delete saved vector store files
            if os.path.exists(config.VECTOR_STORE_PATH):
                shutil.rmtree(config.VECTOR_STORE_PATH)
                print(f"Deleted vector store at {config.VECTOR_STORE_PATH}")
            
            return {
                "success": True,
                "message": "Vector store cleared successfully"
            }
        except Exception as e:
            print(f"Error clearing vector store: {e}")
            return {
                "success": False,
                "message": f"Failed to clear vector store: {str(e)}"
            }
    
    def query(self, question: str) -> dict:
        """Query the RAG system."""
        if not self.is_configured():
            return {
                "answer": "Please configure your Azure OpenAI API key first.",
                "sources": []
            }
        
        if self.vector_store is None or self.retriever is None:
            return {
                "answer": "Vector store not initialized. Please ingest documents first.",
                "sources": []
            }
        
        try:
            # Retrieve relevant documents
            docs = self.retriever.invoke(question)
            
            # Format context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Create prompt
            prompt = ChatPromptTemplate.from_template(
                """You are an AI assistant helping users understand research papers about AI/ML.
Use the following context from research papers to answer the question.
Be concise but thorough in your answer. If the context doesn't contain enough information, say so.

Context:
{context}

Question: {question}

Answer:"""
            )
            
            # Create chain and invoke
            chain = prompt | self.llm | StrOutputParser()
            answer = chain.invoke({"context": context, "question": question})
            
            # Extract unique sources
            sources = list(set([
                doc.metadata.get('source_file', 'Unknown')
                for doc in docs
            ]))
            
            return {
                "answer": answer,
                "sources": sources
            }
        except Exception as e:
            return {
                "answer": f"Error processing query: {str(e)}",
                "sources": []
            }
    
    def ingest_documents(self) -> dict:
        """Full ingestion pipeline from default PDF directory."""
        return self.ingest_from_directory(config.PDF_DIR)
    
    def ingest_from_directory(self, pdf_directory: str) -> dict:
        """Ingest documents from a specific directory."""
        if not self.is_configured():
            return {"success": False, "message": "Please configure your Azure OpenAI API key first."}
        
        print(f"Starting document ingestion from: {pdf_directory}")
        
        # Load PDFs
        documents = self.load_pdfs(pdf_directory)
        if not documents:
            return {"success": False, "message": "No documents found to ingest"}
        
        # Create vector store
        success = self.create_vector_store(documents)
        
        if success:
            return {
                "success": True,
                "message": f"Successfully ingested {len(documents)} document pages"
            }
        else:
            return {"success": False, "message": "Failed to create vector store"}


# Global RAG engine instance
rag_engine = RAGEngine()
