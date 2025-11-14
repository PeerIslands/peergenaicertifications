"""
Unit tests for conversation chain creation functionality.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document


class TestConversationChain:
    """Test cases for create_conversation_chain function."""
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_conversation_chain_success(self, mock_prompt_template, mock_chat_openai):
        """Test successful conversation chain creation."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock prompt template
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        
        # Execute
        result = create_conversation_chain(mock_vector_store)
        
        # Assertions
        assert result is not None
        assert "chain" in result
        assert "retriever" in result
        assert result["retriever"] == mock_retriever
        mock_vector_store.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        mock_chat_openai.assert_called_once_with(temperature=0, model_name="gpt-3.5-turbo")
        mock_prompt_template.from_messages.assert_called()
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_conversation_chain_retriever_config(self, mock_prompt_template, mock_chat_openai):
        """Test that retriever is configured with correct search parameters."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_chat_openai.return_value = Mock()
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Execute
        result = create_conversation_chain(mock_vector_store)
        
        # Assertions
        mock_vector_store.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        assert result["retriever"] == mock_retriever
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_conversation_chain_llm_config(self, mock_prompt_template, mock_chat_openai):
        """Test that LLM is configured with correct parameters."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.as_retriever.return_value = Mock()
        
        # Mock ChatOpenAI
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Execute
        result = create_conversation_chain(mock_vector_store)
        
        # Assertions
        mock_chat_openai.assert_called_once_with(temperature=0, model_name="gpt-3.5-turbo")
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_create_conversation_chain_rag_chain_structure(self, mock_prompt_template, mock_chat_openai):
        """Test that RAG chain has correct structure."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_llm = Mock()
        mock_chat_openai.return_value = mock_llm
        
        # Mock prompt template
        mock_prompt = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        
        # Execute
        result = create_conversation_chain(mock_vector_store)
        
        # Assertions
        assert "chain" in result
        assert "retriever" in result
        # Verify chain is a runnable (has invoke method or similar)
        assert hasattr(result["chain"], "__or__") or hasattr(result["chain"], "invoke")

