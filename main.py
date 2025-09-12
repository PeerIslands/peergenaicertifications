import streamlit as st
import os
from datetime import datetime
from document_processor import DocumentProcessor
from mongodb_client import MongoDBClient
from rag_chatbot import RAGChatbot
from config import OPENAI_API_KEY, MONGODB_URI

# Page configuration
st.set_page_config(
    page_title="RAG Document Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .upload-section {
        background-color: #f0f2f6;
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #667eea;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left-color: #2196f3;
    }
    .bot-message {
        background-color: #f3e5f5;
        border-left-color: #9c27b0;
    }
    .sidebar-section {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
def initialize_session_state():
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'documents_uploaded' not in st.session_state:
        st.session_state.documents_uploaded = 0
    if 'mongodb_connected' not in st.session_state:
        st.session_state.mongodb_connected = False
    if 'chatbot_ready' not in st.session_state:
        st.session_state.chatbot_ready = False

def check_configuration():
    """Check if all required configurations are set"""
    config_issues = []
    
    if not OPENAI_API_KEY:
        config_issues.append("OpenAI API Key is not set")
    
    try:
        # Test MongoDB connection
        mongodb_client = MongoDBClient()
        mongodb_client.close_connection()
        st.session_state.mongodb_connected = True
    except Exception as e:
        config_issues.append(f"MongoDB connection failed: {str(e)}")
        st.session_state.mongodb_connected = False
    
    return config_issues

def display_configuration_status():
    """Display configuration status in sidebar"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("🔧 Configuration Status")
    
    config_issues = check_configuration()
    
    if not config_issues:
        st.sidebar.success("✅ All configurations are set correctly!")
        st.session_state.chatbot_ready = True
    else:
        st.sidebar.error("❌ Configuration Issues:")
        for issue in config_issues:
            st.sidebar.write(f"• {issue}")
        st.session_state.chatbot_ready = False
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("📝 Setup Instructions")
        st.sidebar.write("1. Set your OpenAI API key as an environment variable:")
        st.sidebar.code("export OPENAI_API_KEY='your-api-key'")
        st.sidebar.write("2. Ensure MongoDB is running:")
        st.sidebar.code("mongod --dbpath /path/to/your/db")
        st.sidebar.write("3. Or set custom MongoDB URI:")
        st.sidebar.code("export MONGODB_URI='your-mongodb-uri'")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def upload_documents():
    """Handle document upload and processing"""
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    st.subheader("📄 Upload Documents")
    
    uploaded_files = st.file_uploader(
        "Choose files to upload",
        type=['pdf', 'docx', 'txt'],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT"
    )
    
    if uploaded_files:
        if st.button("Process Documents", type="primary"):
            if not st.session_state.chatbot_ready:
                st.error("Please fix configuration issues before uploading documents.")
                return
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                doc_processor = DocumentProcessor()
                mongodb_client = MongoDBClient()
                
                total_files = len(uploaded_files)
                successful_uploads = 0
                
                for i, uploaded_file in enumerate(uploaded_files):
                    status_text.text(f"Processing {uploaded_file.name}...")
                    progress_bar.progress((i + 1) / total_files)
                    
                    try:
                        # Process document
                        document_data = doc_processor.process_document(uploaded_file)
                        
                        # Store in MongoDB
                        document_id = mongodb_client.store_document(document_data)
                        
                        successful_uploads += 1
                        st.success(f"✅ Successfully processed: {uploaded_file.name}")
                        
                    except Exception as e:
                        st.error(f"❌ Error processing {uploaded_file.name}: {str(e)}")
                
                mongodb_client.close_connection()
                st.session_state.documents_uploaded += successful_uploads
                
                if successful_uploads > 0:
                    st.success(f"🎉 Successfully uploaded {successful_uploads} document(s)!")
                    st.rerun()
                
            except Exception as e:
                st.error(f"Error during document processing: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_document_library():
    """Display uploaded documents in sidebar"""
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.subheader("📚 Document Library")
    
    try:
        mongodb_client = MongoDBClient()
        documents = mongodb_client.get_all_documents()
        mongodb_client.close_connection()
        
        if documents:
            st.sidebar.write(f"Total documents: {len(documents)}")
            
            for doc in documents:
                with st.sidebar.expander(f"📄 {doc['filename'][:30]}..."):
                    st.write(f"**Uploaded:** {doc['timestamp'].strftime('%Y-%m-%d %H:%M')}")
                    st.write(f"**Chunks:** {doc['num_chunks']}")
                    if st.button(f"🗑️ Delete", key=f"delete_{doc['id']}"):
                        try:
                            mongodb_client = MongoDBClient()
                            if mongodb_client.delete_document(doc['id']):
                                st.success("Document deleted!")
                                st.rerun()
                            mongodb_client.close_connection()
                        except Exception as e:
                            st.error(f"Error deleting document: {str(e)}")
            
            if st.sidebar.button("🗑️ Clear All Documents", type="secondary"):
                try:
                    mongodb_client = MongoDBClient()
                    deleted_count = mongodb_client.clear_all_documents()
                    mongodb_client.close_connection()
                    st.sidebar.success(f"Deleted {deleted_count} documents!")
                    st.session_state.chat_history = []
                    st.rerun()
                except Exception as e:
                    st.sidebar.error(f"Error clearing documents: {str(e)}")
        else:
            st.sidebar.info("No documents uploaded yet.")
    
    except Exception as e:
        st.sidebar.error(f"Error loading documents: {str(e)}")
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

def chat_interface():
    """Main chat interface"""
    st.subheader("💬 Chat with Your Documents")
    
    if not st.session_state.chatbot_ready:
        st.warning("⚠️ Please fix configuration issues before using the chat.")
        return
    
    try:
        # Check if there are any documents
        mongodb_client = MongoDBClient()
        documents = mongodb_client.get_all_documents()
        mongodb_client.close_connection()
        
        if not documents:
            st.info("📝 Upload some documents first to start chatting!")
            return
        
        # Initialize chatbot
        rag_chatbot = RAGChatbot()
        
        # Display chat history
        for message in st.session_state.chat_history:
            if message['role'] == 'user':
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong> {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message bot-message"><strong>Assistant:</strong> {message["content"]}</div>', unsafe_allow_html=True)
                
                # Show sources if available
                if 'sources' in message and message['sources']:
                    with st.expander("📚 Sources Used"):
                        for i, source in enumerate(message['sources'], 1):
                            st.write(f"**{i}. {source['filename']}** (Similarity: {source['similarity']:.3f})")
                            st.write(f"_{source['text'][:200]}..._")
                            st.write("---")
        
        # Chat input
        user_input = st.chat_input("Ask a question about your documents...")
        
        if user_input:
            # Add user message to chat history
            st.session_state.chat_history.append({
                'role': 'user',
                'content': user_input
            })
            
            # Generate response
            with st.spinner("Thinking..."):
                try:
                    response_data = rag_chatbot.chat(user_input)
                    
                    # Add assistant response to chat history
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response_data['response'],
                        'sources': response_data['context_used']
                    })
                    
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error generating response: {str(e)}")
        
        # Display conversation starter if chat is empty
        if not st.session_state.chat_history:
            starter_message = rag_chatbot.get_conversation_starter()
            st.info(starter_message)
    
    except Exception as e:
        st.error(f"Error initializing chat: {str(e)}")

def main():
    """Main application"""
    initialize_session_state()
    
    # Header
    st.markdown('<h1 class="main-header">🤖 RAG Document Chat</h1>', unsafe_allow_html=True)
    st.markdown("Upload documents and chat with them using AI-powered search and generation!")
    
    # Sidebar
    display_configuration_status()
    display_document_library()
    
    # Main content
    col1, col2 = st.columns([1, 2])
    
    with col1:
        upload_documents()
    
    with col2:
        chat_interface()
    
    # Footer
    st.markdown("---")
    st.markdown("Built with Streamlit, OpenAI, MongoDB, and Sentence Transformers")

if __name__ == "__main__":
    main()
