import pytest
from unittest.mock import MagicMock, patch
from rag_chatbot import RAGChatbot
import openai


class TestRAGChatbot:

    def test_rag_chatbot_initialization(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        assert chatbot is not None
        assert chatbot.openai_client is not None
        assert chatbot.embedding_model is not None
        assert chatbot.mongodb_client is not None

    def test_rag_chatbot_initialization_without_api_key(
        self, mock_mongodb_client, mock_sentence_transformer
    ):
        with patch("rag_chatbot.OPENAI_API_KEY", ""):
            with pytest.raises(ValueError, match="OpenAI API key not found"):
                RAGChatbot()

    def test_validate_query_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        assert chatbot._validate_query("What is this about?") is True

    def test_validate_query_empty(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(ValueError, match="Query must be a non-empty string"):
            chatbot._validate_query("")

    def test_validate_query_whitespace(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(
            ValueError, match="Query cannot be empty or whitespace only"
        ):
            chatbot._validate_query("   ")

    def test_validate_query_too_short(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(ValueError, match="Query is too short"):
            chatbot._validate_query("hi")

    def test_validate_query_too_long(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        long_query = "a" * 5001
        with pytest.raises(ValueError, match="Query is too long"):
            chatbot._validate_query(long_query)

    def test_generate_query_embedding_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        query = "What is this document about?"
        embedding = chatbot.generate_query_embedding(query)
        assert isinstance(embedding, list)
        assert len(embedding) > 0

    def test_retrieve_relevant_context_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()

        mock_chunks = [
            {"filename": "test.pdf", "text": "test content", "similarity": 0.9}
        ]
        chatbot.mongodb_client.similarity_search = MagicMock(return_value=mock_chunks)

        query = "What is this about?"
        results = chatbot.retrieve_relevant_context(query, top_k=5)
        assert len(results) == 1
        assert results[0]["filename"] == "test.pdf"

    def test_retrieve_relevant_context_invalid_top_k(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(ValueError, match="top_k must be a positive integer"):
            chatbot.retrieve_relevant_context("test query", top_k=0)

    def test_format_context_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        relevant_chunks = [
            {"filename": "test.pdf", "text": "test content", "similarity": 0.9}
        ]
        context = chatbot.format_context(relevant_chunks)
        assert isinstance(context, str)
        assert "test.pdf" in context
        assert "test content" in context

    def test_format_context_empty(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        context = chatbot.format_context([])
        assert "No relevant context found" in context

    def test_format_context_invalid_input(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(RuntimeError, match="Failed to format context"):
            chatbot.format_context("not a list")

    def test_generate_response_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        query = "What is this about?"
        context = "This is test context."
        response = chatbot.generate_response(query, context)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_generate_response_empty_context(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        with pytest.raises(ValueError, match="Context must be a non-empty string"):
            chatbot.generate_response("test query", "")

    def test_chat_success(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()

        mock_chunks = [
            {"filename": "test.pdf", "text": "test content", "similarity": 0.9}
        ]
        chatbot.mongodb_client.similarity_search = MagicMock(return_value=mock_chunks)

        query = "What is this about?"
        result = chatbot.chat(query)

        assert "query" in result
        assert "response" in result
        assert "context_used" in result
        assert "num_sources" in result
        assert result["query"] == query

    def test_chat_with_invalid_query(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        result = chatbot.chat("")
        assert "Invalid input" in result["response"]

    def test_get_conversation_starter_with_documents(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()

        mock_docs = [
            {"filename": "test1.pdf", "timestamp": "2024-01-01", "num_chunks": 5},
            {"filename": "test2.pdf", "timestamp": "2024-01-02", "num_chunks": 3},
        ]
        chatbot.mongodb_client.get_all_documents = MagicMock(return_value=mock_docs)

        starter = chatbot.get_conversation_starter()
        assert isinstance(starter, str)
        assert "test1.pdf" in starter

    def test_get_conversation_starter_without_documents(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        chatbot.mongodb_client.get_all_documents = MagicMock(return_value=[])

        starter = chatbot.get_conversation_starter()
        assert "upload some documents" in starter.lower()

    def test_chat_handles_openai_api_error(
        self, mock_env_vars, mock_mongodb_client, mock_sentence_transformer
    ):
        with patch("openai.OpenAI") as mock_openai:
            mock_client = MagicMock()
            mock_client.chat.completions.create.side_effect = Exception("API Error")
            mock_openai.return_value = mock_client

            chatbot = RAGChatbot()
            mock_chunks = [{"filename": "test.pdf", "text": "test", "similarity": 0.9}]
            chatbot.mongodb_client.similarity_search = MagicMock(
                return_value=mock_chunks
            )

            result = chatbot.chat("test query")
            assert (
                "Error processing" in result["response"]
                or "error" in result["response"].lower()
            )

    def test_retrieve_relevant_context_large_top_k(
        self,
        mock_env_vars,
        mock_mongodb_client,
        mock_sentence_transformer,
        mock_openai_client,
    ):
        chatbot = RAGChatbot()
        mock_chunks = []
        chatbot.mongodb_client.similarity_search = MagicMock(return_value=mock_chunks)

        results = chatbot.retrieve_relevant_context("test query", top_k=150)
        chatbot.mongodb_client.similarity_search.assert_called_once()
