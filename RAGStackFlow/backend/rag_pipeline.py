import os
from typing import List, Dict, Optional
from pathlib import Path
import pickle

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import (
    PyPDFLoader,
    Docx2txtLoader,
    UnstructuredExcelLoader,
    TextLoader,
    CSVLoader,
    UnstructuredMarkdownLoader
)
from langchain_community.vectorstores import FAISS
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ConversationBufferMemory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings, AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from langchain.prompts import PromptTemplate

class RAGPipeline:
    def __init__(self):
        # Azure OpenAI configuration
        self.azure_openai_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_openai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.azure_openai_api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        self.azure_chat_deployment = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT")
        self.azure_embedding_deployment = os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT")
        
        # Fallback to regular OpenAI if Azure not configured
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Other API keys for alternative models
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
        
        # Initialize embeddings - prefer Azure OpenAI
        self.embeddings = None
        if (self.azure_openai_api_key and self.azure_openai_endpoint and 
            self.azure_embedding_deployment):
            self.embeddings = AzureOpenAIEmbeddings(
                azure_deployment=self.azure_embedding_deployment,
                openai_api_version=self.azure_openai_api_version,
                azure_endpoint=self.azure_openai_endpoint,
                api_key=self.azure_openai_api_key
            )
            print("Using Azure OpenAI Embeddings")
        elif self.openai_api_key:
            self.embeddings = OpenAIEmbeddings(
                model="text-embedding-3-large",
                api_key=self.openai_api_key
            )
            print("Using OpenAI Embeddings")
        else:
            raise ValueError("Either Azure OpenAI or OpenAI API key must be configured")
            
        self.vector_store = None
        self.memories = {}
        self.document_metadata = []
        
        self.vector_store_path = Path("data/vector_store/faiss_index")
        self.metadata_path = Path("data/vector_store/metadata.pkl")
        
        self._load_existing_index()
    
    def _load_existing_index(self):
        if self.vector_store_path.exists() and self.metadata_path.exists():
            try:
                if self.embeddings:
                    self.vector_store = FAISS.load_local(
                        str(self.vector_store_path.parent),
                        self.embeddings,
                        "faiss_index"
                    )
                    with open(self.metadata_path, 'rb') as f:
                        self.document_metadata = pickle.load(f)
            except Exception as e:
                print(f"Could not load existing index: {e}")
    
    def _save_index(self):
        if self.vector_store:
            self.vector_store_path.parent.mkdir(parents=True, exist_ok=True)
            self.vector_store.save_local(
                str(self.vector_store_path.parent),
                "faiss_index"
            )
            with open(self.metadata_path, 'wb') as f:
                pickle.dump(self.document_metadata, f)
    
    def _get_loader(self, file_path: str):
        ext = Path(file_path).suffix.lower()
        
        loaders = {
            '.pdf': PyPDFLoader,
            '.docx': Docx2txtLoader,
            '.xlsx': UnstructuredExcelLoader,
            '.txt': TextLoader,
            '.csv': CSVLoader,
            '.md': UnstructuredMarkdownLoader,
        }
        
        if ext in loaders:
            return loaders[ext](file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    async def process_document(self, file_path: str, filename: str) -> Dict:
        if not self.embeddings:
            raise ValueError("Embeddings not configured. Please set either Azure OpenAI or OpenAI API credentials.")
        
        loader = self._get_loader(file_path)
        documents = loader.load()
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1200,  # Increased from 1000
            chunk_overlap=200,  # Increased from 150
            length_function=len,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        chunks = text_splitter.split_documents(documents)
        
        for chunk in chunks:
            chunk.metadata['source'] = filename
        
        if self.vector_store is None:
            self.vector_store = FAISS.from_documents(chunks, self.embeddings)
        else:
            self.vector_store.add_documents(chunks)
        
        self.document_metadata.append({
            'filename': filename,
            'path': file_path,
            'chunks': len(chunks)
        })
        
        self._save_index()
        
        return {
            "chunks_created": len(chunks),
            "filename": filename
        }
    
    def _get_llm(self, model: str):
        if model == "openai":
            # Prefer Azure OpenAI if configured
            if (self.azure_openai_api_key and self.azure_openai_endpoint and 
                self.azure_chat_deployment):
                return AzureChatOpenAI(
                    azure_deployment=self.azure_chat_deployment,
                    openai_api_version=self.azure_openai_api_version,
                    azure_endpoint=self.azure_openai_endpoint,
                    api_key=self.azure_openai_api_key,
                    temperature=0.1,  # Low but not zero for some creativity
                    max_tokens=500  # Limit response length
                )
            elif self.openai_api_key:
                return ChatOpenAI(
                    model="gpt-4o",
                    temperature=0.1,  # Low but not zero for some creativity
                    max_tokens=500,  # Limit response length
                    api_key=self.openai_api_key
                )
            else:
                raise ValueError("Neither Azure OpenAI nor OpenAI API key is configured")
        elif model == "gemini":
            if not self.google_api_key:
                raise ValueError("Google API key not set")
            return ChatGoogleGenerativeAI(
                model="gemini-pro",
                temperature=0,
                google_api_key=self.google_api_key
            )
        elif model == "anthropic":
            if not self.anthropic_api_key:
                raise ValueError("Anthropic API key not set")
            return ChatAnthropic(
                model="claude-3-5-sonnet-20241022",
                temperature=0,
                api_key=self.anthropic_api_key
            )
        else:
            raise ValueError(f"Unknown model: {model}")
    
    def _get_qa_prompt(self):
        template = """You are a helpful AI assistant that explains complex research papers in simple, conversational language. Answer questions based ONLY on the provided document context.

STRICT RULES:
1. Answer ONLY using information from the provided documents
2. Use simple, clear language that matches the example style above
3. Be concise but complete - aim for 1-2 sentences for most questions
4. Use technical terms when they appear in the documents (like "vanishing gradients", "residual connections", "generative models")
5. If the question cannot be answered from the documents, respond with: "I can only answer questions based on the documents you've uploaded. This question appears to be outside the scope of those documents."
6. Focus on key concepts and practical explanations

Context from documents:
{context}

Question: {question}

Answer based only on the context above, using the style and terminology from the examples:"""
        
        return PromptTemplate(
            template=template,
            input_variables=["context", "question"]
        )
    
    def _simplify_response(self, raw_answer: str, question: str) -> str:
        """Light post-processing to ensure response style matches expectations"""
        
        # If it's the fallback response, return as-is
        if "I can only answer questions based on the documents" in raw_answer:
            return raw_answer
        
        # Simple cleanup and style adjustments
        answer = raw_answer.strip()
        
        # Remove excessive technical details but keep key terms
        if len(answer) > 300:  # Only simplify if too long
            # Create a focused simplification prompt
            simplification_prompt = f"""Make this answer more concise while keeping the exact technical terms and key concepts:

Question: {question}
Answer: {answer}

Concise version (keep technical terms like "vanishing gradients", "residual connections", etc.):"""

            try:
                llm = self._get_llm("openai")
                simplified = llm.invoke(simplification_prompt)
                
                if hasattr(simplified, 'content'):
                    simplified_text = simplified.content.strip()
                    # Only use simplified version if it's reasonable length
                    if 50 < len(simplified_text) < 400:
                        return simplified_text
            except:
                pass
        
        return answer
                
    def _check_relevance(self, question: str, retrieved_docs, threshold: float = 0.5) -> tuple[bool, float]:
        if not retrieved_docs or len(retrieved_docs) == 0:
            return False, 0.0
        
        query_embedding = self.embeddings.embed_query(question)
        
        similarities = []
        for doc in retrieved_docs:
            doc_embedding = self.embeddings.embed_query(doc.page_content)
            
            similarity = sum(a * b for a, b in zip(query_embedding, doc_embedding)) / (
                (sum(a * a for a in query_embedding) ** 0.5) * 
                (sum(b * b for b in doc_embedding) ** 0.5)
            )
            similarities.append(similarity)
        
        max_similarity = max(similarities) if similarities else 0.0
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0.0
        
        is_relevant = max_similarity > threshold and avg_similarity > (threshold * 0.7)
        
        return is_relevant, max_similarity
    
    async def chat(self, message: str, model: str = "openai", session_id: str = "default") -> Dict:
        if not self.vector_store:
            raise ValueError("No documents indexed. Please upload documents first.")
        
        llm = self._get_llm(model)
        
        if session_id not in self.memories:
            self.memories[session_id] = ConversationBufferMemory(
                memory_key="chat_history",
                return_messages=True,
                output_key="answer"
            )
        
        retriever = self.vector_store.as_retriever(
            search_type="mmr",
            search_kwargs={
                "k": 6,  # Increased from 4
                "fetch_k": 15,  # Increased from 10
                "lambda_mult": 0.7  # Balance between relevance and diversity
            }
        )
        
        retrieved_docs = retriever.get_relevant_documents(message)
        
        is_relevant, similarity_score = self._check_relevance(message, retrieved_docs)
        
        if not is_relevant:
            return {
                "answer": "I can only answer questions based on the documents you've uploaded. This question appears to be outside the scope of those documents.",
                "sources": [],
                "confidence": 0.0
            }
        
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=retriever,
            memory=self.memories[session_id],
            return_source_documents=True,
            verbose=False,
            combine_docs_chain_kwargs={
                "prompt": self._get_qa_prompt()
            }
        )
        
        result = qa_chain({"question": message})
        
        # Post-process the answer to make it more conversational
        simplified_answer = self._simplify_response(result['answer'], message)
        
        sources = list(set([doc.metadata.get('source', 'unknown') for doc in result['source_documents']]))
        
        doc_count_factor = min(len(result['source_documents']) / 4.0, 1.0)
        combined_confidence = (similarity_score * 0.6) + (doc_count_factor * 0.4)
        
        return {
            "answer": simplified_answer,
            "sources": sources,
            "confidence": round(combined_confidence, 2)
        }
    
    def reset_session(self, session_id: str = "default"):
        if session_id in self.memories:
            del self.memories[session_id]
    
    def has_documents(self) -> bool:
        return self.vector_store is not None
    
    def list_documents(self) -> List[Dict]:
        return self.document_metadata
