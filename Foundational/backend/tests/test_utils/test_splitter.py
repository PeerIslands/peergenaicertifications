"""Tests for text splitter utility."""
import pytest


class TestTextSplitter:
    """Test cases for text splitter."""
    
    def test_split_text_basic(self):
        """Test basic text splitting."""
        from src.utils.splitter import TextSplitter
        
        splitter = TextSplitter(chunk_size=100, chunk_overlap=20)
        text = "This is a test document. " * 20
        
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 0
        assert all(isinstance(chunk, str) for chunk in chunks)
    
    def test_split_empty_text(self):
        """Test splitting empty text."""
        from src.utils.splitter import TextSplitter
        
        splitter = TextSplitter()
        chunks = splitter.split_text("")
        
        assert len(chunks) == 0
    
    def test_split_short_text(self):
        """Test splitting text shorter than chunk size."""
        from src.utils.splitter import TextSplitter
        
        splitter = TextSplitter(chunk_size=1000)
        text = "Short text"
        
        chunks = splitter.split_text(text)
        
        assert len(chunks) == 1
        assert chunks[0] == text
    
    def test_chunk_overlap(self):
        """Test that chunks have proper overlap."""
        from src.utils.splitter import TextSplitter
        
        splitter = TextSplitter(chunk_size=50, chunk_overlap=10)
        text = "A" * 100
        
        chunks = splitter.split_text(text)
        
        assert len(chunks) > 1
        # Verify overlap exists
        if len(chunks) > 1:
            assert chunks[0][-10:] == chunks[1][:10] or len(chunks[1]) < 10

