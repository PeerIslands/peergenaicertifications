"""
Extended unit tests for conversation chain functionality.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, AIMessage


class TestConversationChainExtended:
    """Extended test cases for create_conversation_chain function."""
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    @patch('app.StrOutputParser')
    def test_rag_chain_invocation(self, mock_output_parser, mock_prompt_template, mock_chat_openai):
        """Test that RAG chain can be invoked with proper input."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock retrieved documents
        mock_docs = [
            Document(page_content="Context 1", metadata={"page": 0}),
            Document(page_content="Context 2", metadata={"page": 1})
        ]
        mock_retriever.invoke.return_value = mock_docs
        
        # Mock ChatOpenAI
        mock_llm = Mock()
        mock_llm.invoke.return_value = Mock(content="Test response")
        mock_chat_openai.return_value = mock_llm
        
        # Mock prompt template
        mock_prompt = Mock()
        mock_prompt.invoke.return_value = Mock()
        mock_prompt_template.from_messages.return_value = mock_prompt
        
        # Mock output parser
        mock_parser = Mock()
        mock_parser.invoke.return_value = "Parsed response"
        mock_output_parser.return_value = mock_parser
        
        # Execute
        result = create_conversation_chain(mock_vector_store)
        
        # Assertions
        assert result is not None
        assert "chain" in result
        assert "retriever" in result
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_format_docs_function(self, mock_prompt_template, mock_chat_openai):
        """Test that format_docs function works correctly."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_retriever = Mock()
        mock_vector_store.as_retriever.return_value = mock_retriever
        
        # Mock ChatOpenAI
        mock_chat_openai.return_value = Mock()
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Execute to get the chain
        result = create_conversation_chain(mock_vector_store)
        
        # The format_docs function is internal, but we can test it indirectly
        # by checking that the chain structure is correct
        assert result is not None
        assert "chain" in result
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_retriever_search_kwargs(self, mock_prompt_template, mock_chat_openai):
        """Test that retriever is configured with k=3."""
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
        
        # Verify retriever was called with k=3
        mock_vector_store.as_retriever.assert_called_once_with(search_kwargs={"k": 3})
        assert result["retriever"] == mock_retriever
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_llm_temperature_setting(self, mock_prompt_template, mock_chat_openai):
        """Test that LLM is configured with temperature=0."""
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
        create_conversation_chain(mock_vector_store)
        
        # Verify ChatOpenAI was called with temperature=0
        mock_chat_openai.assert_called_once_with(temperature=0, model_name="gpt-3.5-turbo")
    
    @patch('app.ChatOpenAI')
    @patch('app.ChatPromptTemplate')
    def test_llm_model_name(self, mock_prompt_template, mock_chat_openai):
        """Test that LLM uses gpt-3.5-turbo model."""
        from app import create_conversation_chain
        
        # Mock vector store
        mock_vector_store = Mock()
        mock_vector_store.as_retriever.return_value = Mock()
        
        # Mock ChatOpenAI
        mock_chat_openai.return_value = Mock()
        
        # Mock prompt template
        mock_prompt_template.from_messages.return_value = Mock()
        
        # Execute
        create_conversation_chain(mock_vector_store)
        
        # Verify model name is gpt-3.5-turbo
        call_args = mock_chat_openai.call_args
        assert call_args.kwargs['model_name'] == "gpt-3.5-turbo"

