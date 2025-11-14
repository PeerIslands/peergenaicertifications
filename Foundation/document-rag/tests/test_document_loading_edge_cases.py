"""
Unit tests for document loading edge cases and uncovered paths.
"""
import pytest
from unittest.mock import Mock, patch
from langchain_core.documents import Document


class TestDocumentLoadingEdgeCases:
    """Test cases for edge cases in document loading."""
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_unsupported_file_type_continue(self, mock_unlink, mock_tempfile, mock_loader):
        """Test that unsupported file types trigger continue statement (line 93)."""
        from app import load_documents
        
        # Mock uploaded file with unsupported extension
        mock_file = Mock()
        mock_file.name = "test.xyz"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake content"
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions - should skip unsupported file and continue
        assert len(result) == 0
        # Should not create temp file or call loader for unsupported types
        assert mock_tempfile.call_count == 0
        assert mock_loader.call_count == 0
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_file_with_no_extension(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling of file with no extension."""
        from app import load_documents
        
        # Mock uploaded file with no extension
        mock_file = Mock()
        mock_file.name = "testfile"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake content"
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions - should skip file with no extension
        assert len(result) == 0
        assert mock_tempfile.call_count == 0
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_multiple_unsupported_files(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling multiple unsupported files."""
        from app import load_documents
        
        # Mock uploaded files with unsupported extensions
        mock_file1 = Mock()
        mock_file1.name = "test1.xyz"
        mock_file1.size = 1024
        mock_file1.read.return_value = b"fake content 1"
        
        mock_file2 = Mock()
        mock_file2.name = "test2.abc"
        mock_file2.size = 2048
        mock_file2.read.return_value = b"fake content 2"
        
        # Execute
        result = load_documents([mock_file1, mock_file2])
        
        # Assertions - should skip all unsupported files
        assert len(result) == 0
        assert mock_tempfile.call_count == 0
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_mixed_supported_unsupported_files(self, mock_unlink, mock_tempfile, mock_pdf_loader):
        """Test handling mix of supported and unsupported files."""
        from app import load_documents
        
        # Mock supported file
        mock_pdf = Mock()
        mock_pdf.name = "test.pdf"
        mock_pdf.size = 1024
        mock_pdf.read.return_value = b"pdf content"
        
        # Mock unsupported file
        mock_unsupported = Mock()
        mock_unsupported.name = "test.xyz"
        mock_unsupported.size = 512
        mock_unsupported.read.return_value = b"unsupported content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader
        mock_pdf_doc = Document(page_content="PDF content", metadata={})
        mock_pdf_loader_instance = Mock()
        mock_pdf_loader_instance.load.return_value = [mock_pdf_doc]
        mock_pdf_loader.return_value = mock_pdf_loader_instance
        
        # Execute
        result = load_documents([mock_pdf, mock_unsupported])
        
        # Assertions - should only load supported file
        assert len(result) == 1
        assert result[0].metadata['source_file'] == "test.pdf"
        # Should only create temp file for supported file
        assert mock_tempfile.call_count == 1
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_file_with_dot_in_name(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling of file with dot in name but valid extension."""
        from app import load_documents
        
        # Mock uploaded file with dot in name
        mock_file = Mock()
        mock_file.name = "test.file.pdf"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.file.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader
        mock_doc = Document(page_content="Test content", metadata={"page": 0})
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions - should handle file with dot in name correctly
        assert len(result) == 1
        assert result[0].metadata['source_file'] == "test.file.pdf"
        mock_loader.assert_called_once()

