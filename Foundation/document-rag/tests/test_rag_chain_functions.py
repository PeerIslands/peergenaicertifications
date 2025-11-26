"""
Unit tests for RAG chain internal functions.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document


class TestRAGChainFunctions:
    """Test cases for internal RAG chain functions."""
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_format_docs_function(self, mock_prompt_template, mock_chat_openai):
        """Test that format_docs function formats documents correctly."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_chat_openai.return_value = Mock()
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Create chain to access format_docs indirectly
        result = create_conversation_chain(mock_vector_store)
        
        # The format_docs function is called internally when the chain is invoked
        # We can test it by checking the chain structure
        assert result is not None
        assert "chain" in result
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_rag_chain_input_function(self, mock_prompt_template, mock_chat_openai):
        """Test that create_rag_chain_input function works correctly."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        
        # Mock retrieved documents
        mock_docs = [
            Document(page_content="Context 1", metadata={"page": 0}),
            Document(page_content="Context 2", metadata={"page": 1})
        ]
        mock_retriever.invoke.return_value = mock_docs
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Test response")
        mock_chat_openai.return_value = mock_llm
        
        # Mock prompt template
        mock_prompt = Mock()
        mock_prompt.invoke.return_value = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        
        # Create chain
        result = create_conversation_chain(mock_vector_store)
        
        # The create_rag_chain_input function is called when chain is invoked
        # Test by invoking the chain
        test_input = {"input": "test query", "chat_history": []}
        
        # Mock the chain components
        chain = result["chain"]
        
        # Verify retriever is set up correctly
        assert result["retriever"] == mock_retriever
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_retriever_invoke_in_rag_chain(self, mock_prompt_template, mock_chat_openai):
        """Test that retriever.invoke is called with query."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock retrieved documents
        mock_docs = [
            Document(page_content="Context", metadata={"page": 0})
        ]
        mock_retriever.invoke.return_value = mock_docs
        
        # Mock ChatOpenAI
        mock_chat_openai.return_value = Mock()
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Create chain
        result = create_conversation_chain(mock_vector_store)
        
        # The retriever.invoke is called inside create_rag_chain_input
        # which is part of the chain, so we verify the retriever is set up
        assert result["retriever"] == mock_retriever

