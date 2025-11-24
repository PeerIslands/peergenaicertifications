import streamlit as st
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_mongodb import MongoDBAtlasVectorSearch
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from langchain_core.documents import Document
import tempfile
import os
import logging
from typing import List
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('document_rag.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(
    page_title="Document RAG Chat",
    page_icon="📚",
    layout="wide"
)

# Initialize session state
if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "messages" not in st.session_state:
    st.session_state.messages = []
if "conversation_chain" not in st.session_state:
    st.session_state.conversation_chain = None
if "uploaded_files" not in st.session_state:
    st.session_state.uploaded_files = []
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mongodb_uri" not in st.session_state:
    st.session_state.mongodb_uri = ""
if "mongodb_db" not in st.session_state:
    st.session_state.mongodb_db = "document_rag"
if "mongodb_collection" not in st.session_state:
    st.session_state.mongodb_collection = "documents"
if "mongodb_index" not in st.session_state:
    st.session_state.mongodb_index = "vector_index"

def load_documents(uploaded_files: List) -> List:
    """Load and extract text from uploaded documents (PDF, DOCX, TXT)."""
    logger.info(f"Starting document loading process for {len(uploaded_files)} file(s)")
    all_documents = []
    
    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        file_ext = os.path.splitext(file_name)[1].lower()
        logger.info(f"Processing file: {file_name} (size: {uploaded_file.size} bytes, type: {file_ext})")
        
        # Determine file extension and appropriate suffix
        if file_ext == '.pdf':
            suffix = '.pdf'
        elif file_ext == '.docx':
            suffix = '.docx'
        elif file_ext == '.txt':
            suffix = '.txt'
        else:
            logger.warning(f"Unsupported file type: {file_ext} for file {file_name}")
            st.warning(f"Unsupported file type: {file_ext} for file {file_name}. Skipping...")
            continue
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
            tmp_file.write(uploaded_file.read())
            tmp_path = tmp_file.name
        
        try:
            logger.debug(f"Created temporary file: {tmp_path}")
            
            # Load document based on file type
            logger.info(f"Loading content from {file_name}")
            if file_ext == '.pdf':
                loader = PyPDFLoader(tmp_path)
            elif file_ext == '.docx':
                loader = Docx2txtLoader(tmp_path)
            elif file_ext == '.txt':
                loader = TextLoader(tmp_path, encoding='utf-8')
            else:
                continue
            
            documents = loader.load()
            
            # Add source file name to metadata for each document
            for doc in documents:
                doc.metadata['source_file'] = file_name
            
            logger.info(f"Successfully loaded {len(documents)} document chunk(s) from {file_name}")
            all_documents.extend(documents)
            
            # Log document statistics
            total_chars = sum(len(doc.page_content) for doc in documents)
            logger.debug(f"Total characters extracted from {file_name}: {total_chars}")
            
        except Exception as e:
            logger.error(f"Error loading {file_name}: {str(e)}", exc_info=True)
            st.error(f"Error loading {file_name}: {str(e)}")
        finally:
            # Clean up temporary file
            try:
                os.unlink(tmp_path)
                logger.debug(f"Cleaned up temporary file: {tmp_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {tmp_path}: {str(e)}")
    
    logger.info(f"Document loading complete. Total documents loaded: {len(all_documents)}")
    return all_documents

def create_vector_store(documents: List, mongodb_uri: str, db_name: str, collection_name: str, index_name: str):
    """Create a MongoDB vector store from documents."""
    logger.info("Starting MongoDB vector store creation")
    
    if not documents:
        logger.warning("No documents provided for vector store creation")
        return None
    
    if not mongodb_uri:
        logger.error("MongoDB connection string is required")
        return None
    
    logger.info(f"Processing {len(documents)} document(s) for vector store")
    
    # Split documents into chunks
    logger.info("Splitting documents into chunks (chunk_size=1000, chunk_overlap=200)")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    logger.info(f"Created {len(chunks)} chunk(s) from {len(documents)} document(s)")
    
    # Log chunk statistics
    total_chunk_chars = sum(len(chunk.page_content) for chunk in chunks)
    avg_chunk_size = total_chunk_chars / len(chunks) if chunks else 0
    logger.debug(f"Average chunk size: {avg_chunk_size:.0f} characters")
    
    # Filter metadata to only include allowed fields
    allowed_metadata_fields = {'total_pages', 'page', 'page_label', 'source_file'}
    logger.info("Filtering metadata to include only allowed fields")
    filtered_chunks = []
    for chunk in chunks:
        # Create new metadata dict with only allowed fields
        filtered_metadata = {
            key: value 
            for key, value in chunk.metadata.items() 
            if key in allowed_metadata_fields
        }
        # Create a new document with filtered metadata
        filtered_chunk = Document(
            page_content=chunk.page_content,
            metadata=filtered_metadata
        )
        filtered_chunks.append(filtered_chunk)
    
    logger.info(f"Filtered {len(filtered_chunks)} chunk(s) metadata")
    
    # Create embeddings
    logger.info("Initializing OpenAI embeddings")
    embeddings = OpenAIEmbeddings()
    
    # Create MongoDB vector store
    logger.info(f"Connecting to MongoDB: {db_name}.{collection_name}")
    try:
        vector_store = MongoDBAtlasVectorSearch.from_connection_string(
            connection_string=mongodb_uri,
            namespace=f"{db_name}.{collection_name}",
            embedding=embeddings,
            index_name=index_name
        )
        
        logger.info("Adding documents to MongoDB vector store")
        # Add documents to the vector store (only allowed fields will be stored)
        vector_store.add_documents(filtered_chunks)
        
        logger.info(f"MongoDB vector store created successfully with {len(chunks)} embedded chunk(s)")
        logger.info(f"Documents stored in: {db_name}.{collection_name}")
        
        return vector_store
        
    except Exception as e:
        logger.error(f"Error creating MongoDB vector store: {str(e)}", exc_info=True)
        raise

def create_conversation_chain(vector_store):
    """Create a conversational retrieval chain using LangChain 1.0."""
    logger.info("Creating conversational retrieval chain")
    
    logger.info("Initializing ChatOpenAI model (gpt-3.5-turbo, temperature=0)")
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo")
    
    logger.info("Creating retriever from vector store (k=3)")
    retriever = vector_store.as_retriever(search_kwargs={"k": 3})
    
    # Create the QA prompt
    logger.debug("Creating QA prompt template")
    qa_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Use the following pieces of retrieved context "
         "to answer the question. If you don't know the answer, just say that you don't know. "
         "Use three sentences maximum and keep the answer concise.\n\n"
         "Context: {context}"),
        MessagesPlaceholder("chat_history"),
        ("human", "{input}")
    ])
    
    # Format documents function
    def format_docs(docs):
        formatted = "\n\n".join(doc.page_content for doc in docs)
        logger.debug(f"Formatted {len(docs)} document(s) into context string ({len(formatted)} chars)")
        return formatted
    
    # Create the RAG chain
    def create_rag_chain_input(input_dict):
        query = input_dict["input"]
        logger.debug(f"Retrieving documents for query: {query[:100]}...")
        
        # Retrieve documents based on input
        docs = retriever.invoke(query)
        logger.info(f"Retrieved {len(docs)} document(s) for query")
        
        return {
            "context": format_docs(docs),
            "input": query,
            "chat_history": input_dict.get("chat_history", [])
        }
    
    logger.info("Building RAG chain pipeline")
    rag_chain = (
        RunnablePassthrough() | create_rag_chain_input
        | qa_prompt
        | llm
        | StrOutputParser()
    )
    
    logger.info("Conversational retrieval chain created successfully")
    return {"chain": rag_chain, "retriever": retriever}

# Layout: Left column for document upload, Center for chat
col1, col2 = st.columns([1, 3])

# Left column for document upload
with col1:
    st.header("📄 Upload Documents")
    
    # API Key input
    st.subheader("🔑 Configuration")
    api_key = st.text_input(
        "OpenAI API Key",
        type="password",
        help="Enter your OpenAI API key",
        value=st.session_state.api_key
    )
    if api_key:
        os.environ["OPENAI_API_KEY"] = api_key
        st.session_state.api_key = api_key
    
    st.divider()
    
    # MongoDB Configuration
    st.subheader("🗄️ MongoDB Configuration")
    mongodb_uri = st.text_input(
        "MongoDB Connection String",
        type="password",
        help="Enter your MongoDB Atlas connection string (mongodb+srv://...)",
        value=st.session_state.mongodb_uri,
        placeholder="mongodb+srv://user:pass@cluster.mongodb.net/"
    )
    if mongodb_uri:
        st.session_state.mongodb_uri = mongodb_uri
    
    mongodb_db = st.text_input(
        "Database Name",
        value=st.session_state.mongodb_db,
        help="Name of the MongoDB database"
    )
    # Always update session state with current input value when user provides input
    if mongodb_db and mongodb_db.strip():
        st.session_state.mongodb_db = mongodb_db.strip()
    
    mongodb_collection = st.text_input(
        "Collection Name",
        value=st.session_state.mongodb_collection,
        help="Name of the MongoDB collection"
    )
    # Always update session state with current input value when user provides input
    if mongodb_collection and mongodb_collection.strip():
        st.session_state.mongodb_collection = mongodb_collection.strip()
    
    mongodb_index = st.text_input(
        "Vector Index Name",
        value=st.session_state.mongodb_index,
        help="Name of the vector search index in MongoDB Atlas"
    )
    # Always update session state with current input value when user provides input
    if mongodb_index and mongodb_index.strip():
        st.session_state.mongodb_index = mongodb_index.strip()
    
    st.divider()
    
    uploaded_files = st.file_uploader(
        "Choose documents",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True,
        help="Upload one or more documents (PDF, DOCX, TXT) to chat with"
    )
    
    if st.button("Process Documents", type="primary", use_container_width=True):
        if uploaded_files:
            if not st.session_state.api_key:
                st.error("Please enter your OpenAI API key first!")
            else:
                if not st.session_state.mongodb_uri:
                    st.error("Please enter your MongoDB connection string first!")
                else:
                    with st.spinner("Processing documents..."):
                        logger.info("=" * 50)
                        logger.info("Starting document processing workflow")
                        logger.info(f"Processing {len(uploaded_files)} file(s)")
                        
                        # Get current values from inputs (use session state as fallback)
                        db_name = mongodb_db.strip() if mongodb_db and mongodb_db.strip() else st.session_state.mongodb_db
                        collection_name = mongodb_collection.strip() if mongodb_collection and mongodb_collection.strip() else st.session_state.mongodb_collection
                        index_name = mongodb_index.strip() if mongodb_index and mongodb_index.strip() else st.session_state.mongodb_index
                        
                        logger.info(f"Using database: {db_name}, collection: {collection_name}, index: {index_name}")
                        
                        # Load documents
                        documents = load_documents(uploaded_files)
                        
                        if documents:
                            try:
                                # Create vector store using current input values
                                st.session_state.vector_store = create_vector_store(
                                    documents,
                                    st.session_state.mongodb_uri,
                                    db_name,
                                    collection_name,
                                    index_name
                                )
                                
                                if st.session_state.vector_store:
                                    # Create conversation chain
                                    st.session_state.conversation_chain = create_conversation_chain(
                                        st.session_state.vector_store
                                    )
                                    
                                    # Store uploaded file names
                                    st.session_state.uploaded_files = [f.name for f in uploaded_files]
                                    
                                    logger.info("Document processing workflow completed successfully")
                                    logger.info(f"Processed files: {', '.join(st.session_state.uploaded_files)}")
                                    logger.info("=" * 50)
                                    
                                    st.success(f"Successfully processed {len(uploaded_files)} document(s)!")
                                    st.session_state.messages = []  # Reset chat history
                                else:
                                    logger.error("Vector store creation failed")
                                    st.error("Failed to create vector store.")
                            except Exception as e:
                                logger.error(f"Error creating vector store: {str(e)}", exc_info=True)
                                st.error(f"Error creating vector store: {str(e)}")
                        else:
                            logger.error("No documents could be loaded from the uploaded files")
                            st.error("No documents could be loaded from the uploaded files.")
        else:
            st.warning("Please upload at least one document file.")
    
    # Display uploaded files
    if st.session_state.uploaded_files:
        st.divider()
        st.subheader("📚 Loaded Documents")
        for file_name in st.session_state.uploaded_files:
            st.write(f"• {file_name}")
    
    # Clear chat button
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Center column for chat
with col2:
    st.title("📚 Document RAG Chat")
    
    if not st.session_state.uploaded_files:
        st.info("👈 Upload documents in the left column to get started!")
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            # Detailed source documents in expander
            if "sources" in message and message["sources"]:
                with st.expander("📄 Source Documents"):
                    for i, source in enumerate(message["sources"], 1):
                        st.write(f"**Source {i}:**")
                        doc_title = source.metadata.get('source_file', source.metadata.get('source', 'Unknown Document'))
                        st.write(f"**Document:** {doc_title}")
                        st.write(f"**Page:** {source.metadata.get('page', 'N/A')}")
                        st.write(f"**Content:** {source.page_content[:200]}...")
                        st.divider()

    # Chat input - must be at the end to appear at bottom
    if prompt := st.chat_input("Ask a question about the uploaded documents..."):
        # Check if documents are processed
        if st.session_state.conversation_chain is None:
            st.warning("⚠️ Please upload and process documents first!")
            st.rerun()
        elif not st.session_state.api_key:
            st.warning("⚠️ Please enter your OpenAI API key first!")
            st.rerun()
        else:
            # Add user message to chat history first
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Process the query
            with st.spinner("Thinking..."):
                try:
                    logger.info("=" * 50)
                    logger.info(f"Processing chat query: {prompt[:100]}...")
                    start_time = datetime.now()
                    
                    # Format chat history for the chain (list of Message objects)
                    logger.debug("Formatting chat history")
                    chat_history = []
                    for i in range(0, len(st.session_state.messages) - 1, 2):
                        if i + 1 < len(st.session_state.messages):
                            user_msg = st.session_state.messages[i]
                            assistant_msg = st.session_state.messages[i + 1]
                            if user_msg["role"] == "user" and assistant_msg["role"] == "assistant":
                                chat_history.append(HumanMessage(content=user_msg["content"]))
                                chat_history.append(AIMessage(content=assistant_msg["content"]))
                    
                    logger.info(f"Chat history contains {len(chat_history)} message(s)")
                    
                    # Get the chain and retriever
                    chain = st.session_state.conversation_chain["chain"]
                    retriever = st.session_state.conversation_chain["retriever"]
                    
                    # Retrieve source documents
                    logger.info("Retrieving relevant documents from vector store")
                    retrieval_start = datetime.now()
                    sources = retriever.invoke(prompt)
                    retrieval_time = (datetime.now() - retrieval_start).total_seconds()
                    logger.info(f"Document retrieval completed in {retrieval_time:.2f}s - found {len(sources)} document(s)")
                    
                    # Log source document details
                    for i, source in enumerate(sources, 1):
                        page = source.metadata.get('page', 'N/A')
                        source_preview = source.page_content[:100].replace('\n', ' ')
                        logger.debug(f"Source {i}: Page {page} - {source_preview}...")
                    
                    # Invoke the chain
                    logger.info("Invoking RAG chain to generate response")
                    chain_start = datetime.now()
                    answer = chain.invoke({
                        "input": prompt,
                        "chat_history": chat_history
                    })
                    chain_time = (datetime.now() - chain_start).total_seconds()
                    
                    total_time = (datetime.now() - start_time).total_seconds()
                    logger.info(f"Response generation completed in {chain_time:.2f}s")
                    logger.info(f"Total query processing time: {total_time:.2f}s")
                    logger.info(f"Generated response length: {len(answer)} characters")
                    logger.info("=" * 50)
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "sources": sources
                    })
                    
                except Exception as e:
                    logger.error(f"Error processing chat query: {str(e)}", exc_info=True)
                    error_msg = f"Error: {str(e)}"
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })
            
            # Rerun to display the new messages
            st.rerun()

