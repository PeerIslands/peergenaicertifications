"""
Enhanced RAG service with LlamaIndex integration for advanced document processing and querying.
"""
# Suppress warnings before imports
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*pydantic.*", category=UserWarning)

import logging
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
import time

# LangChain imports (keeping existing functionality)
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document as LangChainDocument
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_openai import OpenAIEmbeddings

# LlamaIndex imports
from llama_index.core import VectorStoreIndex, QueryBundle
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.postprocessor import SimilarityPostprocessor, MetadataReplacementPostProcessor
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.mongodb import MongoDBAtlasVectorSearch as LlamaMongoVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.core import Settings
import pymongo

from ..utils.document_processor import DocumentProcessor
from ..utils.llamaindex_processor import LlamaIndexProcessor
from ..config.settings import settings
from ..utils.logging_config import get_logger
from ..utils.metrics import (
    track_document_processed, track_question_answered, 
    track_llm_cost, track_operation_duration, track_error,
    indexed_documents_total, conversation_history_size
)
from ..utils.tracing import trace_function, add_span_attributes

# Configure logging
logger = get_logger(__name__)


class EnhancedRAGService:
    """
    Enhanced RAG service that combines LangChain and LlamaIndex capabilities
    for superior document processing and question answering.
    """
    
    def __init__(self):
        """Initialize the enhanced RAG service with both LangChain and LlamaIndex."""
        
        # Initialize processors
        self.document_processor = DocumentProcessor()
        
        # Initialize LlamaIndex processor lazily (only if API key is available)
        self.llamaindex_processor = None
        self._llamaindex_available = False
        
        try:
            if settings.openai_api_key:
                self.llamaindex_processor = LlamaIndexProcessor()
                self._llamaindex_available = True
                logger.info("LlamaIndex processor initialized successfully")
            else:
                logger.warning(
                    "OPENAI_API_KEY not found. LlamaIndex features will be unavailable. "
                    "Set OPENAI_API_KEY environment variable to enable LlamaIndex processing."
                )
        except Exception as e:
            logger.warning(f"Failed to initialize LlamaIndex processor: {str(e)}. LangChain will be used as fallback.")
        
        # Initialize MongoDB client (with graceful error handling)
        self.mongodb_client = None
        self._mongodb_available = False
        
        try:
            # Test MongoDB connection with a short timeout
            self.mongodb_client = pymongo.MongoClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            # Test the connection
            self.mongodb_client.server_info()
            self._mongodb_available = True
            logger.info(f"MongoDB connection established: {settings.mongodb_database}")
        except Exception as e:
            logger.warning(
                f"MongoDB connection failed: {str(e)}. "
                f"Please check your MONGODB_URI in .env file. "
                f"Using local MongoDB or MongoDB Atlas? Update MONGODB_URI accordingly."
            )
            # Create a dummy client to prevent None errors
            try:
                self.mongodb_client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
            except:
                pass
        
        # LangChain components (for backward compatibility)
        # These require OpenAI API key, so initialize only if available
        self.embeddings = None
        self.langchain_vector_store = None
        self._langchain_available = False
        
        if settings.openai_api_key:
            try:
                # Set environment variable to avoid 'proxies' argument issues
                import os
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
                
                # Initialize embeddings with error handling for version compatibility
                # Use environment variable instead of passing api_key directly
                # Try minimal initialization to avoid 'proxies' argument issues
                try:
                    self.embeddings = OpenAIEmbeddings()
                except Exception as emb_error:
                    logger.debug(f"OpenAIEmbeddings() failed: {str(emb_error)}")
                    # This version has the 'proxies' bug, embeddings won't work
                    self.embeddings = None
                
                # Only create vector store if MongoDB is available and embeddings initialized
                if self._mongodb_available and self.embeddings:
                    try:
                        self.langchain_vector_store = MongoDBAtlasVectorSearch.from_connection_string(
                            connection_string=settings.mongodb_uri,
                            namespace=f"{settings.mongodb_database}.{settings.mongodb_collection}",
                            embedding=self.embeddings,
                            index_name=settings.vector_index_name,
                            text_key="text",
                            embedding_key="embedding"
                        )
                        self._langchain_available = True
                        logger.info("LangChain components initialized successfully")
                    except Exception as vs_error:
                        logger.warning(f"Failed to create LangChain vector store: {str(vs_error)}")
                        self._langchain_available = False
                elif not self._mongodb_available:
                    logger.warning("LangChain vector store not initialized (MongoDB unavailable)")
                elif not self.embeddings:
                    logger.warning("LangChain vector store not initialized (embeddings unavailable)")
            except Exception as e:
                logger.warning(f"Failed to initialize LangChain components: {str(e)}")
        else:
            logger.warning(
                "OPENAI_API_KEY not found. LangChain features will be unavailable. "
                "Set OPENAI_API_KEY environment variable to enable document processing."
            )
        
        # LlamaIndex components (only if MongoDB is available)
        self.llamaindex_vector_store = None
        self.storage_context = None
        
        if self._mongodb_available and self.mongodb_client:
            try:
                # Initialize vector store with error handling for Pydantic compatibility
                try:
                    self.llamaindex_vector_store = LlamaMongoVectorStore(
                        mongodb_client=self.mongodb_client,
                        db_name=settings.mongodb_database,
                        collection_name=settings.mongodb_collection,
                        index_name=settings.vector_index_name
                    )
                    
                    self.storage_context = StorageContext.from_defaults(
                        vector_store=self.llamaindex_vector_store
                    )
                    logger.info("LlamaIndex vector store initialized")
                except (AttributeError, TypeError) as pydantic_error:
                    # Handle Pydantic compatibility issues
                    # Create a basic storage context without MongoDB vector store
                    logger.debug(
                        f"LlamaIndex MongoDB vector store has compatibility issue: {str(pydantic_error)}. "
                        f"Creating basic storage context for document processing."
                    )
                    # Create storage context without vector store (will use default simple store)
                    self.storage_context = StorageContext.from_defaults()
                    self.llamaindex_vector_store = None
                    logger.info("LlamaIndex storage context initialized (in-memory mode)")
            except Exception as e:
                logger.warning(f"Failed to initialize LlamaIndex vector store: {str(e)}")
                # Create fallback storage context
                try:
                    self.storage_context = StorageContext.from_defaults()
                    logger.info("Fallback storage context created")
                except Exception:
                    pass  # If fallback fails, storage_context remains None
        
        # Initialize LLM (only if API key is available)
        self.llm = None
        if settings.openai_api_key:
            try:
                # Ensure environment variable is set (already set above, but ensure it's still set)
                import os
                os.environ["OPENAI_API_KEY"] = settings.openai_api_key
                
                # Workaround for 'proxies' argument error - monkey patch OpenAI client if needed
                try:
                    from openai import OpenAI as OpenAIClient
                    # Check if we can create a client without proxies
                    test_client = OpenAIClient(api_key=settings.openai_api_key)
                    del test_client
                except Exception:
                    pass  # Continue anyway
                
                # Try standard initialization first - use environment variable
                llm_initialized = False
                llm_methods = [
                    lambda: ChatOpenAI(model=settings.llm_model, temperature=settings.temperature, max_tokens=settings.max_tokens),
                    lambda: ChatOpenAI(model_name=settings.llm_model, temperature=settings.temperature, max_tokens=settings.max_tokens),
                    lambda: ChatOpenAI(temperature=settings.temperature, max_tokens=settings.max_tokens),
                    lambda: ChatOpenAI(),
                ]
                
                for llm_method in llm_methods:
                    try:
                        self.llm = llm_method()
                        llm_initialized = True
                        break
                    except Exception as llm_error:
                        error_str = str(llm_error)
                        if "proxies" in error_str.lower():
                            logger.debug(f"Skipping LLM init method due to proxies error")
                            continue
                        logger.debug(f"LLM initialization attempt failed: {error_str}")
                        continue
                
                if llm_initialized:
                    logger.info(f"LLM initialized: {settings.llm_model}")
                else:
                    logger.warning(f"Failed to initialize LLM - evaluation features will be unavailable")
                    self.llm = None
            except Exception as e:
                logger.warning(f"Failed to initialize LLM: {str(e)}")
                self.llm = None
        else:
            logger.warning("LLM not initialized (OPENAI_API_KEY required)")
        
        # LlamaIndex query engine (will be set when index is created)
        self.query_engine = None
        self.vector_index = None
        
        # Conversation history
        self.conversation_history = []
        
        logger.info("Enhanced RAG service initialized with LlamaIndex integration")
    
    def load_and_index_documents_llamaindex(self, 
                                           file_path: Optional[str] = None,
                                           directory_path: Optional[str] = None,
                                           original_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Load and index documents using LlamaIndex for enhanced processing.
        
        Args:
            file_path: Path to a single PDF file
            directory_path: Path to directory containing PDF files
            original_filename: Original filename to store in metadata (for uploaded files)
            
        Returns:
            Dictionary with indexing results and statistics
            
        Raises:
            ValueError: If LlamaIndex processor is not available (missing OPENAI_API_KEY)
        """
        if not self._llamaindex_available or self.llamaindex_processor is None:
            raise ValueError(
                "LlamaIndex processor is not available. "
                "Please set OPENAI_API_KEY environment variable to enable LlamaIndex features."
            )
        
        try:
            start_time = time.time()
            
            # Process documents using LlamaIndex
            if file_path:
                logger.info(f"Processing single PDF with LlamaIndex: {original_filename or file_path}")
                result = self.llamaindex_processor.process_pdf(file_path, original_filename)
            elif directory_path:
                logger.info(f"Processing PDFs from directory with LlamaIndex: {directory_path}")
                result = self.llamaindex_processor.process_pdf_directory(directory_path)
            else:
                raise ValueError("Either file_path or directory_path must be provided")
            
            if not result["success"]:
                return result
            
            documents = result["documents"]
            nodes = result["nodes"]
            
            # Check if storage context is available
            if not self.storage_context:
                return {
                    "success": False,
                    "message": "MongoDB storage context not available. Please check MongoDB connection.",
                    "error": "Storage context not initialized"
                }
            
            # Create or update vector index
            if self.vector_index is None:
                logger.info("Creating new vector index...")
                self.vector_index = VectorStoreIndex(
                    nodes,
                    storage_context=self.storage_context,
                    transformations=[self.llamaindex_processor.node_parser]  # Using transformations instead of deprecated methods
                )
            else:
                logger.info("Adding documents to existing index...")
                self.vector_index.insert_nodes(nodes)
            
            # Create query engine
            self._create_query_engine()
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "message": f"Successfully indexed {len(documents)} documents with {len(nodes)} nodes using LlamaIndex",
                "document_stats": result["stats"],
                "processing_time": round(processing_time, 2),
                "index_type": "llamaindex",
                "total_nodes": len(nodes),
                "original_filename": original_filename
            }
            
        except Exception as e:
            logger.error(f"Error indexing documents with LlamaIndex: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to index documents: {str(e)}",
                "error": str(e)
            }
    
    def load_and_index_documents_langchain(self, 
                                          file_path: Optional[str] = None,
                                          directory_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load and index documents using LangChain (legacy method for compatibility).
        
        Args:
            file_path: Path to a single PDF file
            directory_path: Path to directory containing PDF files
            
        Returns:
            Dictionary with indexing results and statistics
        """
        if not self._langchain_available or not self.langchain_vector_store:
            return {
                "success": False,
                "message": "LangChain components not available. Please set OPENAI_API_KEY and ensure MongoDB is connected.",
                "error": "LangChain components not initialized"
            }
        
        try:
            start_time = time.time()
            
            # Load documents using LangChain processor
            if file_path:
                logger.info(f"Loading single PDF with LangChain: {file_path}")
                documents = self.document_processor.process_pdf(file_path)
            elif directory_path:
                logger.info(f"Loading PDFs from directory with LangChain: {directory_path}")
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
                    "source_type": "pdf",
                    "processor": "langchain"
                })
            
            # Index documents in vector store
            doc_ids = self.langchain_vector_store.add_documents(documents)
            
            # Get statistics
            doc_stats = self.document_processor.get_document_stats(documents)
            
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "message": f"Successfully indexed {len(documents)} document chunks using LangChain",
                "document_ids": doc_ids,
                "document_stats": doc_stats,
                "processing_time": round(processing_time, 2),
                "index_type": "langchain"
            }
            
        except Exception as e:
            logger.error(f"Error indexing documents with LangChain: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to index documents: {str(e)}",
                "error": str(e)
            }
    
    @trace_function(span_name="load_and_index_documents")
    def load_and_index_documents(self, 
                                file_path: Optional[str] = None,
                                directory_path: Optional[str] = None,
                                use_llamaindex: bool = True,
                                original_filename: Optional[str] = None) -> Dict[str, Any]:
        """
        Load and index documents using the specified processor.
        
        Args:
            file_path: Path to a single PDF file
            directory_path: Path to directory containing PDF files
            use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False)
            original_filename: Original filename to store in metadata (for uploaded files)
            
        Returns:
            Dictionary with indexing results and statistics
            
        Note:
            If LlamaIndex is requested but not available (missing OPENAI_API_KEY),
            will automatically fall back to LangChain processing.
        """
        framework = "llamaindex" if use_llamaindex else "langchain"
        add_span_attributes(framework=framework, file_path=file_path or directory_path)
        
        start_time = time.time()
        
        try:
            if use_llamaindex and not self._llamaindex_available:
                logger.warning(
                    "LlamaIndex requested but not available",
                    framework="llamaindex",
                    fallback="langchain"
                )
                use_llamaindex = False
                framework = "langchain"
            
            with track_operation_duration("document_processing", {"framework": framework}):
                if use_llamaindex:
                    result = self.load_and_index_documents_llamaindex(file_path, directory_path, original_filename)
                else:
                    result = self.load_and_index_documents_langchain(file_path, directory_path)
            
            # Track metrics
            if result.get("success"):
                track_document_processed(
                    framework=framework,
                    status="success",
                    chunks=result.get("num_chunks", 0)
                )
                indexed_documents_total.labels(framework=framework).set(
                    result.get("num_documents", 0)
                )
            else:
                track_document_processed(framework=framework, status="error")
                track_error("document_processing_failed", "enhanced_rag_service")
            
            return result
            
        except Exception as e:
            track_document_processed(framework=framework, status="error")
            track_error("document_processing_exception", "enhanced_rag_service")
            logger.error("Document processing failed", error=str(e), framework=framework)
            raise
    
    def _create_query_engine(self):
        """Create a query engine with Sentence Window Retrieval from the vector index."""
        if self.vector_index is None:
            logger.warning("No vector index available to create query engine")
            return
        
        try:
            # Create retriever
            retriever = VectorIndexRetriever(
                index=self.vector_index,
                similarity_top_k=settings.top_k_results
            )
            
            # Create postprocessors
            # NOTE: MetadataReplacementPostProcessor is temporarily disabled due to compatibility issues
            # The SentenceWindowNodeParser still creates the window context in metadata,
            # but we're not using it for replacement yet
            
            # SimilarityPostprocessor: Filters results by similarity score
            similarity_filter = SimilarityPostprocessor(
                similarity_cutoff=settings.similarity_threshold
            )
            
            # Create query engine with postprocessors
            # TODO: Re-enable MetadataReplacementPostProcessor once metadata access issues are resolved
            self.query_engine = RetrieverQueryEngine(
                retriever=retriever,
                node_postprocessors=[similarity_filter]
            )
            
            logger.info(f"Query engine created (Sentence Window parsing active with window_size={settings.sentence_window_size}, but not using MetadataReplacement yet)")
            
        except Exception as e:
            logger.error(f"Error creating query engine: {str(e)}")
            raise
    
    def ask_question_llamaindex(self, 
                               question: str,
                               use_conversation_history: bool = False) -> Dict[str, Any]:
        """
        Answer a question using LlamaIndex query engine.
        
        Args:
            question: The question to answer
            use_conversation_history: Whether to include conversation context
            
        Returns:
            Dictionary containing the answer and metadata
            
        Raises:
            ValueError: If LlamaIndex processor is not available
        """
        if not self._llamaindex_available or self.llamaindex_processor is None:
            raise ValueError(
                "LlamaIndex processor is not available. "
                "Please set OPENAI_API_KEY environment variable to enable LlamaIndex features."
            )
        
        if self.query_engine is None:
            return {
                "success": False,
                "message": "No documents indexed with LlamaIndex. Upload documents with use_llamaindex=true or query with use_llamaindex=false.",
                "answer": "No documents indexed with LlamaIndex. Please upload documents with use_llamaindex=true or switch to use_llamaindex=false to use LangChain.",
                "sources": [],
                "num_sources": 0,
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "query_engine": "llamaindex",
                "conversation_history_used": use_conversation_history,
                "error": "No LlamaIndex documents - use use_llamaindex=false or upload with use_llamaindex=true"
            }
        
        try:
            start_time = time.time()
            
            # Prepare query with conversation history if requested
            if use_conversation_history and self.conversation_history:
                context = self._format_conversation_history()
                enhanced_question = f"Previous conversation context:\n{context}\n\nCurrent question: {question}"
            else:
                enhanced_question = question
            
            # Query the index
            try:
                response = self.query_engine.query(enhanced_question)
            except KeyError as key_error:
                # This likely means documents were indexed with LangChain but querying with LlamaIndex
                # or vice versa - missing expected metadata fields like "window"
                logger.error(f"KeyError during query: {str(key_error)} - Documents may have been indexed with a different processor")
                return {
                    "success": False,
                    "message": f"Query failed: Missing expected metadata field {str(key_error)}. Documents may need to be re-indexed.",
                    "answer": "Unable to process query. The documents may need to be re-indexed with the current processor.",
                    "sources": [],
                    "num_sources": 0,
                    "processing_time": round(time.time() - start_time, 2),
                    "timestamp": datetime.now().isoformat(),
                    "query_engine": "llamaindex",
                    "conversation_history_used": use_conversation_history,
                    "error": f"KeyError: {str(key_error)}"
                }
            except Exception as query_error:
                logger.error(f"Query execution error: {str(query_error)}")
                raise
            
            processing_time = time.time() - start_time
            
            # Extract source information
            sources = []
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for idx, node in enumerate(response.source_nodes):
                    try:
                        # Safely get metadata and text
                        node_metadata = getattr(node, 'metadata', {}) or {}
                        
                        # Try multiple ways to get text content
                        if hasattr(node, 'text'):
                            node_text = node.text
                        elif hasattr(node, 'get_content'):
                            node_text = node.get_content()
                        elif hasattr(node, 'node') and hasattr(node.node, 'text'):
                            node_text = node.node.text
                        else:
                            node_text = str(node)
                        
                        sources.append({
                            "chunk_id": node_metadata.get("chunk_id", idx),
                            "content_preview": node_text[:200] + "..." if len(node_text) > 200 else node_text,
                            "metadata": node_metadata,
                            "score": getattr(node, 'score', None)
                        })
                    except Exception as node_error:
                        logger.warning(f"Error extracting source node {idx}: {str(node_error)}")
                        # Skip this node but continue with others
                        continue
            
            # Update conversation history
            if use_conversation_history:
                # Add user question
                self.conversation_history.append({
                    "type": "human",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                # Add AI response
                self.conversation_history.append({
                    "type": "ai",
                    "content": str(response),
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "answer": str(response),
                "sources": sources,
                "num_sources": len(sources),
                "processing_time": round(processing_time, 2),
                "timestamp": datetime.now().isoformat(),
                "query_engine": "llamaindex",
                "conversation_history_used": use_conversation_history
            }
            
        except Exception as e:
            logger.error(f"Error answering question with LlamaIndex: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to answer question: {str(e)}",
                "answer": "Error processing query. Please try again or contact support.",
                "sources": [],
                "num_sources": 0,
                "processing_time": round(time.time() - start_time, 2),
                "timestamp": datetime.now().isoformat(),
                "query_engine": "llamaindex",
                "conversation_history_used": use_conversation_history,
                "error": str(e)
            }
    
    def ask_question_langchain(self, 
                              question: str,
                              k: int = None,
                              use_conversation_history: bool = False) -> Dict[str, Any]:
        """
        Answer a question using LangChain (legacy method for compatibility).
        
        Args:
            question: The question to answer
            k: Number of documents to retrieve
            use_conversation_history: Whether to include conversation context
            
        Returns:
            Dictionary containing the answer and metadata
        """
        if not self._langchain_available or not self.llm or not self.langchain_vector_store:
            return {
                "success": False,
                "answer": "LangChain components not available. Please set OPENAI_API_KEY and ensure MongoDB is connected.",
                "sources": [],
                "num_sources": 0,
                "processing_time": 0.0,
                "timestamp": datetime.now().isoformat(),
                "query_engine": "langchain",
                "conversation_history_used": use_conversation_history,
                "error": "LangChain components not initialized"
            }
        
        try:
            start_time = time.time()
            k = k or settings.top_k_results
            
            # Retrieve relevant documents
            retriever = self.langchain_vector_store.as_retriever(
                search_kwargs={"k": k}
            )
            relevant_docs = retriever.get_relevant_documents(question)
            
            if not relevant_docs:
                return {
                    "answer": "I couldn't find any relevant information to answer your question.",
                    "sources": [],
                    "num_sources": 0,
                    "processing_time": 0,
                    "query_engine": "langchain"
                }
            
            # Prepare context
            context = "\n\n".join([doc.page_content for doc in relevant_docs])
            
            # Prepare prompt based on conversation history usage
            if use_conversation_history and self.conversation_history:
                chat_history = self._format_conversation_history()
                prompt = f"""You are a professional AI assistant. Provide clear, direct, and accurate answers.

Context:
{context}

Conversation History:
{chat_history}

Question: {question}

Instructions:
- Answer directly and professionally
- Use information only from the provided context
- Be concise and specific
- If uncertain, state it clearly

Answer:"""
            else:
                prompt = f"""You are a professional AI assistant. Provide clear, direct answers based on the context.

Context:
{context}

Question: {question}

Instructions:
- Answer directly and professionally
- Use only information from the context above
- Be concise and specific
- State facts without unnecessary politeness

Answer:"""
            
            # Generate answer
            response = self.llm.invoke(prompt)
            answer = response.content
            
            processing_time = time.time() - start_time
            
            # Prepare source information
            sources = []
            for idx, doc in enumerate(relevant_docs):
                sources.append({
                    "chunk_id": doc.metadata.get("chunk_id", idx),
                    "content_preview": doc.page_content[:200] + "..." if len(doc.page_content) > 200 else doc.page_content,
                    "metadata": doc.metadata
                })
            
            # Update conversation history
            if use_conversation_history:
                # Add user question
                self.conversation_history.append({
                    "type": "human",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                # Add AI response
                self.conversation_history.append({
                    "type": "ai",
                    "content": answer,
                    "timestamp": datetime.now().isoformat()
                })
            
            return {
                "success": True,
                "answer": answer,
                "sources": sources,
                "num_sources": len(sources),
                "processing_time": round(processing_time, 2),
                "timestamp": datetime.now().isoformat(),
                "query_engine": "langchain",
                "conversation_history_used": use_conversation_history
            }
            
        except Exception as e:
            logger.error(f"Error answering question with LangChain: {str(e)}")
            return {
                "success": False,
                "message": f"Failed to answer question: {str(e)}",
                "answer": "Error processing query. Please try again or contact support.",
                "sources": [],
                "num_sources": 0,
                "processing_time": round(time.time() - start_time, 2),
                "timestamp": datetime.now().isoformat(),
                "query_engine": "langchain",
                "conversation_history_used": use_conversation_history,
                "error": str(e)
            }
    
    @trace_function(span_name="ask_question")
    def ask_question(self, 
                    question: str,
                    k: int = None,
                    use_conversation_history: bool = False,
                    use_llamaindex: bool = True) -> Dict[str, Any]:
        """
        Answer a question using the specified query engine.
        
        Args:
            question: The question to answer
            k: Number of documents to retrieve (for LangChain)
            use_conversation_history: Whether to include conversation context
            use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False)
            
        Returns:
            Dictionary containing the answer and metadata
            
        Note:
            If LlamaIndex is requested but not available (missing OPENAI_API_KEY),
            will automatically fall back to LangChain processing.
        """
        framework = "llamaindex" if use_llamaindex else "langchain"
        add_span_attributes(
            framework=framework,
            question_length=len(question),
            use_conversation_history=use_conversation_history
        )
        
        try:
            if use_llamaindex and not self._llamaindex_available:
                logger.warning(
                    "LlamaIndex requested but not available",
                    framework="llamaindex",
                    fallback="langchain"
                )
                use_llamaindex = False
                framework = "langchain"
            
            with track_operation_duration("question_answering", {"framework": framework}):
                if use_llamaindex:
                    try:
                        result = self.ask_question_llamaindex(question, use_conversation_history)
                    except ValueError as e:
                        logger.warning("LlamaIndex query failed", error=str(e), fallback="langchain")
                        result = self.ask_question_langchain(question, k, use_conversation_history)
                        framework = "langchain"
                else:
                    result = self.ask_question_langchain(question, k, use_conversation_history)
            
            # Track metrics
            if result.get("success"):
                track_question_answered(framework=framework, status="success")
                # Track token usage if available in response (requires instrumentation of LLM calls)
                add_span_attributes(
                    answer_length=len(result.get("answer", "")),
                    num_sources=result.get("num_sources", 0),
                    processing_time=result.get("processing_time", 0)
                )
            else:
                track_question_answered(framework=framework, status="error")
                track_error("question_answering_failed", "enhanced_rag_service")
            
            # Update conversation history size metric
            conversation_history_size.set(len(self.conversation_history))
            
            return result
            
        except Exception as e:
            track_question_answered(framework=framework, status="error")
            track_error("question_answering_exception", "enhanced_rag_service")
            logger.error("Question answering failed", error=str(e), framework=framework)
            raise
    
    def _format_conversation_history(self) -> str:
        """Format conversation history for context."""
        if not self.conversation_history:
            return ""
        
        formatted_history = []
        for entry in self.conversation_history[-10:]:  # Last 10 messages (5 exchanges)
            if entry['type'] == 'human':
                formatted_history.append(f"Q: {entry['content']}")
            else:  # ai
                formatted_history.append(f"A: {entry['content']}")
        
        return "\n".join(formatted_history)
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get the conversation history."""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self):
        """Clear the conversation history."""
        self.conversation_history.clear()
        conversation_history_size.set(0)
        logger.info("Conversation history cleared")
    
    def get_service_stats(self) -> Dict[str, Any]:
        """Get service statistics and configuration."""
        try:
            # Basic configuration stats
            stats = {
                "llm_model": settings.llm_model,  # Will show gpt-3.5-turbo from your .env
                "embedding_model": settings.embedding_model,  # Will show text-embedding-ada-002 from your .env
                "chunk_size": settings.chunk_size,
                "chunk_overlap": settings.chunk_overlap,
                "top_k_results": settings.top_k_results,
                "similarity_threshold": settings.similarity_threshold,
                "conversation_history_length": len(self.conversation_history),
                
                # Approach availability
                "available_approaches": {
                    "llamaindex": {
                        "available": self.query_engine is not None,
                        "description": "Advanced document processing with LlamaIndex",
                        "features": [
                            "Better PDF parsing",
                            "Advanced chunking strategies", 
                            "Sophisticated query engine",
                            "Rich metadata handling",
                            "Non-deprecated APIs"
                        ]
                    },
                    "langchain": {
                        "available": True,
                        "description": "Traditional document processing with LangChain",
                        "features": [
                            "Standard PDF processing",
                            "Basic text splitting",
                            "Simple retrieval",
                            "Basic metadata",
                            "Backward compatibility"
                        ]
                    }
                },
                
                # Default approach
                "default_approach": "llamaindex",
                
                # Processing capabilities
                "processing_capabilities": {
                    "single_file_upload": True,
                    "multiple_file_upload": True,
                    "directory_processing": True,
                    "original_filename_preservation": True,
                    "conversation_history": True,
                    "similarity_filtering": True
                }
            }
            
            # Vector store stats
            try:
                db = self.mongodb_client[settings.mongodb_database]
                collection = db[settings.mongodb_collection]
                doc_count = collection.count_documents({})
                
                # Get sample documents to show approach differences
                sample_docs = list(collection.find({}, {"metadata": 1}).limit(2))
                
                stats["vector_store_stats"] = {
                    "status": "connected",
                    "type": "MongoDB Atlas",
                    "document_count": doc_count,
                    "database": settings.mongodb_database,
                    "collection": settings.mongodb_collection,
                    "sample_metadata_structure": [doc.get("metadata", {}) for doc in sample_docs]
                }
            except Exception as e:
                stats["vector_store_stats"] = {
                    "status": "error",
                    "error": str(e)
                }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting service stats: {str(e)}")
            return {"error": str(e)}
    
    def __del__(self):
        """Cleanup MongoDB connection."""
        try:
            if hasattr(self, 'mongodb_client'):
                self.mongodb_client.close()
        except:
            pass
