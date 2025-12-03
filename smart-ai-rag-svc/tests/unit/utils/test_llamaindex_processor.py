"""
Unit tests for LlamaIndexProcessor.
"""
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from src.utils.llamaindex_processor import LlamaIndexProcessor


class TestLlamaIndexProcessor:
    """Test LlamaIndexProcessor class."""
    
    @pytest.fixture
    def processor(self, mock_env_vars):
        """Create LlamaIndexProcessor instance."""
        with patch('src.utils.llamaindex_processor.Settings'), \
             patch('src.utils.llamaindex_processor.OpenAI'), \
             patch('src.utils.llamaindex_processor.OpenAIEmbedding'), \
             patch('src.utils.llamaindex_processor.SentenceWindowNodeParser'), \
             patch('src.utils.llamaindex_processor.PDFReader'), \
             patch('src.utils.llamaindex_processor.settings') as mock_settings:
            # Ensure settings has required attributes
            mock_settings.openai_api_key = "sk-test-key"
            mock_settings.llm_model = "gpt-3.5-turbo"
            mock_settings.embedding_model = "text-embedding-ada-002"
            mock_settings.temperature = 0.7
            mock_settings.max_tokens = 1000
            mock_settings.sentence_window_size = 3
            processor = LlamaIndexProcessor()
            yield processor
    
    def test_initialization(self, processor):
        """Test processor initialization."""
        assert processor.node_parser is not None
        assert processor.pdf_reader is not None
    
    def test_load_pdf(self, processor, temp_pdf_file):
        """Test loading a PDF file."""
        processor.pdf_reader.load_data = MagicMock(return_value=[
            MagicMock(text="Test content", metadata={})
        ])
        
        documents = processor.load_pdf(temp_pdf_file)
        
        assert len(documents) > 0
        assert documents[0].metadata["file_name"] is not None
    
    def test_load_pdf_file_not_found(self, processor):
        """Test loading non-existent PDF."""
        with pytest.raises(FileNotFoundError):
            processor.load_pdf("/nonexistent/file.pdf")
    
    def test_create_nodes(self, processor):
        """Test creating nodes from documents."""
        mock_doc = MagicMock()
        mock_doc.text = "Test document content"
        documents = [mock_doc]
        
        processor.node_parser.get_nodes_from_documents = MagicMock(
            return_value=[MagicMock(), MagicMock()]
        )
        
        nodes = processor.create_nodes(documents)
        
        assert len(nodes) == 2
    
    def test_get_processing_stats(self, processor):
        """Test getting processing statistics."""
        mock_doc = MagicMock()
        mock_doc.text = "Test content"
        documents = [mock_doc]
        
        stats = processor.get_processing_stats(documents)
        
        assert "total_documents" in stats
        assert stats["total_documents"] == 1
        assert "total_characters" in stats

