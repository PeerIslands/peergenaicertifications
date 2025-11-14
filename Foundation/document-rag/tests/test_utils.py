"""
Utility tests and helper functions.
"""
import pytest
from langchain_core.documents import Document


class TestDocumentMetadata:
    """Test cases for document metadata handling."""
    
    def test_source_file_metadata(self):
        """Test that source_file metadata is correctly set."""
        doc = Document(
            page_content="Test content",
            metadata={"page": 0}
        )
        doc.metadata['source_file'] = "test.pdf"
        
        assert doc.metadata['source_file'] == "test.pdf"
        assert doc.metadata['page'] == 0
    
    def test_multiple_source_files(self):
        """Test handling documents from multiple source files."""
        doc1 = Document(
            page_content="Content 1",
            metadata={"page": 0, "source_file": "file1.pdf"}
        )
        doc2 = Document(
            page_content="Content 2",
            metadata={"page": 0, "source_file": "file2.pdf"}
        )
        
        assert doc1.metadata['source_file'] == "file1.pdf"
        assert doc2.metadata['source_file'] == "file2.pdf"
        assert doc1.metadata['source_file'] != doc2.metadata['source_file']


class TestDocumentChunking:
    """Test cases for document chunking logic."""
    
    def test_chunk_size_validation(self):
        """Test that chunk size is reasonable."""
        from app import RecursiveCharacterTextSplitter
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        assert splitter._chunk_size == 1000
        assert splitter._chunk_overlap == 200
        assert splitter._chunk_overlap < splitter._chunk_size
    
    def test_document_splitting(self):
        """Test that long documents are split correctly."""
        from app import RecursiveCharacterTextSplitter
        
        # Create a long document
        long_content = " ".join(["word"] * 5000)  # Very long content
        doc = Document(
            page_content=long_content,
            metadata={"page": 0, "source_file": "test.pdf"}
        )
        
        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )
        
        chunks = splitter.split_documents([doc])
        
        # Assertions
        assert len(chunks) > 1  # Should be split into multiple chunks
        for chunk in chunks:
            assert len(chunk.page_content) <= 1000 + 200  # Allow some flexibility
            assert 'source_file' in chunk.metadata  # Metadata should be preserved

