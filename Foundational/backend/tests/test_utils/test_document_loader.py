"""Tests for document loader utility."""
import pytest
from unittest.mock import Mock, patch
from io import BytesIO


class TestDocumentLoader:
    """Test cases for document loader."""
    
    def test_load_pdf_success(self, sample_pdf_file):
        """Test successful PDF loading."""
        from src.utils.document_loader import DocumentLoader
        
        loader = DocumentLoader()
        file_obj = BytesIO(sample_pdf_file)
        
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test content"
            mock_reader.return_value.pages = [mock_page]
            
            text = loader.load_pdf(file_obj)
            
            assert text is not None
            assert isinstance(text, str)
    
    def test_load_empty_pdf(self):
        """Test loading empty PDF."""
        from src.utils.document_loader import DocumentLoader
        
        loader = DocumentLoader()
        empty_file = BytesIO(b"")
        
        with pytest.raises(Exception):
            loader.load_pdf(empty_file)
    
    def test_extract_text_with_multiple_pages(self, sample_pdf_file):
        """Test extracting text from multiple pages."""
        from src.utils.document_loader import DocumentLoader
        
        loader = DocumentLoader()
        file_obj = BytesIO(sample_pdf_file)
        
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page1 = Mock()
            mock_page1.extract_text.return_value = "Page 1 content"
            mock_page2 = Mock()
            mock_page2.extract_text.return_value = "Page 2 content"
            mock_reader.return_value.pages = [mock_page1, mock_page2]
            
            text = loader.load_pdf(file_obj)
            
            assert "Page 1 content" in text
            assert "Page 2 content" in text

