"""
RAG (Retrieval-Augmented Generation) service implementation.
"""
import logging
from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime

from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage
from langchain_core.prompts import PromptTemplate
from langchain.chains import RetrievalQA
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain.memory import ConversationBufferMemory

from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings
from ..utils.document_processor import DocumentProcessor
from ..config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RAGService:
    """
    Retrieval-Augmented Generation service that combines document retrieval 
    with LLM generation for question answering.
    """
    
    def __init__(self, 
                 document_processor: Optional[DocumentProcessor] = None):
        """
        Initialize the RAG service.
        
        Args:
            document_processor: Document processor instance
        """
        self.document_processor = document_processor or DocumentProcessor()
        
        # Initialize OpenAI embeddings
        self.embeddings = OpenAIEmbeddings(
            openai_api_key=settings.openai_api_key,
            model=settings.embedding_model
        )
        
        # Initialize MongoDB Atlas Vector Search
        self.vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=settings.mongodb_uri,
            namespace=f"{settings.mongodb_database}.{settings.mongodb_collection}",
            embedding=self.embeddings,
            index_name="vector_index",
            text_key="text",
            embedding_key="embedding"
        )
        
        # Initialize OpenAI LLM
        self.llm = ChatOpenAI(
            openai_api_key=settings.openai_api_key,
            model_name=settings.llm_model,
            temperature=settings.temperature,
            max_tokens=settings.max_tokens
        )
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # RAG prompt template
        self.rag_prompt = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful AI assistant that answers questions based on the provided context. 
Use the following pieces of context to answer the question at the end. If you don't know the answer based on the context, just say that you don't know, don't try to make up an answer.

Context:
{context}

Question: {question}

Answer: """
        )
        
        # Conversation prompt template
        self.conversation_prompt = PromptTemplate(
            input_variables=["context", "chat_history", "question"],
            template="""You are a helpful AI assistant that answers questions based on the provided context and conversation history.
Use the following pieces of context and chat history to answer the question. If you don't know the answer based on the context, just say that you don't know.

Context:
{context}

Chat History:
{chat_history}

Question: {question}

Answer: """
        )
    
    def load_and_index_documents(self, 
                                file_path: Optional[str] = None,
                                directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load PDF documents and index them in the vector store.
        
        Args:
            file_path: Path to a single PDF file
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary with indexing results and statistics
        """
        try:
            # Load documents
            if file_path:
                logger.info(f"Loading single PDF: {file_path}")
                documents = self.document_processor.process_pdf(file_path)
            elif directory_path:
                logger.info(f"Loading PDFs from directory: {directory_path}")
                documents = self.document_processor.process_pdf_directory(directory_path)
            else:
                raise ValueError("Either file_path or directory_path must be provided")
            
            if not documents:
                return {"success": False, "message": "No documents were loaded"}
            
            # Add metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "chunk_id": i,
                    "indexed_at": datetime.now().isoformat(),
                    "source_type": "pdf"
                })
            
            # Index documents in vector store
            doc_ids = self.vector_store.add_documents(documents)
            
            # Get statistics
            doc_stats = self.document_processor.get_document_stats(documents)
            
            result = {
                "success": True,
                "message": f"Successfully indexed {len(documents)} document chunks",
                "document_ids": doc_ids,
                "document_stats": doc_stats,
                "collection_stats": {"total_documents": len(documents)}
            }
            
            logger.info(f"Indexing completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to load and index documents: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def load_and_index_documents_from_objects(self, documents: List[Document]) -> Dict[str, Any]:
        """
        Load and index documents from a list of Document objects.
        
        Args:
            documents: List of LangChain Document objects
            
        Returns:
            Dictionary with indexing results
        """
        try:
            if not documents:
                return {"success": False, "message": "No documents were provided"}
            
            # Add metadata
            for i, doc in enumerate(documents):
                doc.metadata.update({
                    "chunk_id": i,
                    "indexed_at": datetime.now().isoformat(),
                    "source_type": "document_objects"
                })
            
            # Index documents in vector store
            doc_ids = self.vector_store.add_documents(documents)
            
            # Get statistics
            doc_stats = self.document_processor.get_document_stats(documents)
            
            result = {
                "success": True,
                "message": f"Successfully indexed {len(documents)} document chunks",
                "document_ids": doc_ids,
                "document_stats": doc_stats,
                "collection_stats": {"total_documents": len(documents)}
            }
            
            logger.info(f"Document indexing completed: {result['message']}")
            return result
            
        except Exception as e:
            error_msg = f"Failed to index document objects: {str(e)}"
            logger.error(error_msg)
            return {"success": False, "message": error_msg}
    
    def retrieve_relevant_documents(self, 
                                  query: str, 
                                  k: Optional[int] = None,
                                  include_scores: bool = False) -> List[Document]:
        """
        Retrieve relevant documents for a given query.
        
        Args:
            query: Search query
            k: Number of documents to retrieve
            include_scores: Whether to include similarity scores
            
        Returns:
            List of relevant documents
        """
        try:
            k = k or settings.top_k_results
            
            if include_scores:
                results = self.vector_store.similarity_search_with_score(query, k)
                documents = [doc for doc, score in results]
                logger.info(f"Retrieved {len(documents)} documents with scores")
            else:
                documents = self.vector_store.similarity_search(query, k)
                logger.info(f"Retrieved {len(documents)} relevant documents")
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            return []
    
    def generate_answer(self, 
                       question: str, 
                       context_documents: List[Document],
                       use_conversation_history: bool = False) -> str:
        """
        Generate an answer using the LLM based on retrieved context.
        
        Args:
            question: User question
            context_documents: Retrieved relevant documents
            use_conversation_history: Whether to include conversation history
            
        Returns:
            Generated answer
        """
        try:
            # Prepare context from documents
            context = "\n\n".join([doc.page_content for doc in context_documents])
            
            if use_conversation_history:
                # Get chat history
                chat_history = self.memory.chat_memory.messages
                history_text = "\n".join([
                    f"{'Human' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
                    for msg in chat_history[-6:]  # Last 3 exchanges
                ])
                
                # Format prompt with history
                prompt = self.conversation_prompt.format(
                    context=context,
                    chat_history=history_text,
                    question=question
                )
            else:
                # Format prompt without history
                prompt = self.rag_prompt.format(
                    context=context,
                    question=question
                )
            
            # Generate response
            messages = [SystemMessage(content="You are a helpful AI assistant."),
                       HumanMessage(content=prompt)]
            
            response = self.llm(messages)
            answer = response.content
            
            # Save to memory if using conversation history
            if use_conversation_history:
                self.memory.chat_memory.add_user_message(question)
                self.memory.chat_memory.add_ai_message(answer)
            
            logger.info("Successfully generated answer")
            return answer
            
        except Exception as e:
            error_msg = f"Failed to generate answer: {str(e)}"
            logger.error(error_msg)
            return f"I apologize, but I encountered an error while generating the answer: {error_msg}"
    
    def ask_question(self, 
                    question: str, 
                    k: Optional[int] = None,
                    use_conversation_history: bool = False) -> Dict[str, Any]:
        """
        Complete RAG pipeline: retrieve relevant documents and generate answer.
        
        Args:
            question: User question
            k: Number of documents to retrieve
            use_conversation_history: Whether to use conversation history
            
        Returns:
            Dictionary containing answer and metadata
        """
        start_time = datetime.now()
        
        try:
            logger.info(f"Processing question: '{question[:100]}...'")
            
            # Retrieve relevant documents
            relevant_docs = self.retrieve_relevant_documents(
                query=question, 
                k=k, 
                include_scores=True
            )
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "num_sources": 0,
                    "processing_time": (datetime.now() - start_time).total_seconds(),
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate answer
            answer = self.generate_answer(
                question=question,
                context_documents=relevant_docs,
                use_conversation_history=use_conversation_history
            )
            
            # Prepare source information
            sources = []
            for i, doc in enumerate(relevant_docs):
                source_info = {
                    "chunk_id": i,
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                }
                sources.append(source_info)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            result = {
                "answer": answer,
                "sources": sources,
                "num_sources": len(sources),
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat()
            }
            
            logger.info(f"Question processed successfully in {processing_time:.2f} seconds")
            return result
            
        except Exception as e:
            error_msg = f"Failed to process question: {str(e)}"
            logger.error(error_msg)
            return {
                "answer": f"I apologize, but I encountered an error: {error_msg}",
                "sources": [],
                "num_sources": 0,
                "processing_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
                "error": error_msg
            }
    
    def clear_conversation_history(self) -> None:
        """Clear the conversation memory."""
        self.memory.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """
        Get the current conversation history.
        
        Returns:
            List of conversation messages
        """
        messages = self.memory.chat_memory.messages
        history = []
        
        for msg in messages:
            history.append({
                "type": "human" if isinstance(msg, HumanMessage) else "ai",
                "content": msg.content,
                "timestamp": datetime.now().isoformat()
            })
        
        return history
    
    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the RAG service.
        
        Returns:
            Dictionary containing service statistics
        """
        try:
            return {
                "llm_model": settings.llm_model,
                "embedding_model": settings.embedding_model,
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "top_k_results": settings.top_k_results,
                "similarity_threshold": settings.similarity_threshold,
                "conversation_history_length": len(self.memory.chat_memory.messages),
                "vector_store_stats": {"status": "connected", "type": "MongoDB Atlas"}
            }
            
        except Exception as e:
            logger.error(f"Failed to get service stats: {str(e)}")
            return {"error": str(e)}
