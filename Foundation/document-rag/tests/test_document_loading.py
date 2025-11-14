"""
Unit tests for document loading functionality.
"""
import pytest
import tempfile
import os
from unittest.mock import Mock, patch, MagicMock
from langchain_core.documents import Document


class TestDocumentLoading:
    """Test cases for load_documents function."""
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_single_pdf_success(self, mock_unlink, mock_tempfile, mock_loader):
        """Test successful loading of a single PDF file."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader
        mock_doc = Document(
            page_content="Test content",
            metadata={"page": 0}
        )
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 1
        assert result[0].page_content == "Test content"
        assert result[0].metadata['source_file'] == "test.pdf"
        mock_loader.assert_called_once()
        mock_unlink.assert_called_once()
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_multiple_pdfs(self, mock_unlink, mock_tempfile, mock_loader):
        """Test loading multiple PDF files."""
        from app import load_documents
        
        # Mock uploaded files
        mock_file1 = Mock()
        mock_file1.name = "test1.pdf"
        mock_file1.size = 1024
        mock_file1.read.return_value = b"fake pdf content 1"
        
        mock_file2 = Mock()
        mock_file2.name = "test2.pdf"
        mock_file2.size = 2048
        mock_file2.read.return_value = b"fake pdf content 2"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader
        mock_doc1 = Document(page_content="Content 1", metadata={"page": 0})
        mock_doc2 = Document(page_content="Content 2", metadata={"page": 0})
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = [[mock_doc1], [mock_doc2]]
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file1, mock_file2])
        
        # Assertions
        assert len(result) == 2
        assert result[0].metadata['source_file'] == "test1.pdf"
        assert result[1].metadata['source_file'] == "test2.pdf"
        assert mock_loader.call_count == 2
    
    @patch('app.Docx2txtLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_single_docx_success(self, mock_unlink, mock_tempfile, mock_loader):
        """Test successful loading of a single DOCX file."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.docx"
        mock_file.size = 2048
        mock_file.read.return_value = b"fake docx content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.docx"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock DOCX loader
        mock_doc = Document(
            page_content="Test DOCX content",
            metadata={}
        )
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 1
        assert result[0].page_content == "Test DOCX content"
        assert result[0].metadata['source_file'] == "test.docx"
        mock_loader.assert_called_once()
        mock_unlink.assert_called_once()
    
    @patch('app.TextLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_single_txt_success(self, mock_unlink, mock_tempfile, mock_loader):
        """Test successful loading of a single TXT file."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.txt"
        mock_file.size = 512
        mock_file.read.return_value = b"fake txt content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.txt"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock TXT loader
        mock_doc = Document(
            page_content="Test TXT content",
            metadata={}
        )
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 1
        assert result[0].page_content == "Test TXT content"
        assert result[0].metadata['source_file'] == "test.txt"
        mock_loader.assert_called_once_with("/tmp/test.txt", encoding='utf-8')
        mock_unlink.assert_called_once()
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_mixed_file_types(self, mock_unlink, mock_tempfile, mock_pdf_loader):
        """Test loading mixed file types (PDF, DOCX, TXT)."""
        from app import load_documents
        
        # Mock files
        mock_pdf = Mock()
        mock_pdf.name = "test.pdf"
        mock_pdf.size = 1024
        mock_pdf.read.return_value = b"pdf content"
        
        mock_docx = Mock()
        mock_docx.name = "test.docx"
        mock_docx.size = 2048
        mock_docx.read.return_value = b"docx content"
        
        mock_txt = Mock()
        mock_txt.name = "test.txt"
        mock_txt.size = 512
        mock_txt.read.return_value = b"txt content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock loaders
        with patch('app.Docx2txtLoader') as mock_docx_loader, \
             patch('app.TextLoader') as mock_txt_loader:
            
            mock_pdf_doc = Document(page_content="PDF content", metadata={})
            mock_docx_doc = Document(page_content="DOCX content", metadata={})
            mock_txt_doc = Document(page_content="TXT content", metadata={})
            
            mock_pdf_loader_instance = Mock()
            mock_pdf_loader_instance.load.return_value = [mock_pdf_doc]
            mock_pdf_loader.return_value = mock_pdf_loader_instance
            
            mock_docx_loader_instance = Mock()
            mock_docx_loader_instance.load.return_value = [mock_docx_doc]
            mock_docx_loader.return_value = mock_docx_loader_instance
            
            mock_txt_loader_instance = Mock()
            mock_txt_loader_instance.load.return_value = [mock_txt_doc]
            mock_txt_loader.return_value = mock_txt_loader_instance
            
            # Execute
            result = load_documents([mock_pdf, mock_docx, mock_txt])
            
            # Assertions
            assert len(result) == 3
            assert result[0].metadata['source_file'] == "test.pdf"
            assert result[1].metadata['source_file'] == "test.docx"
            assert result[2].metadata['source_file'] == "test.txt"
            assert mock_pdf_loader.call_count == 1
            assert mock_docx_loader.call_count == 1
            assert mock_txt_loader.call_count == 1
    
    @patch('app.tempfile.NamedTemporaryFile')
    def test_load_unsupported_file_type(self, mock_tempfile):
        """Test handling of unsupported file types."""
        from app import load_documents
        
        # Mock uploaded file with unsupported extension
        mock_file = Mock()
        mock_file.name = "test.xyz"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake content"
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 0
        # Temporary file should not be created for unsupported types
        assert mock_tempfile.call_count == 0
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_pdf_with_error(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling of PDF loading errors."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader to raise exception
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("PDF loading error")
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 0
        mock_unlink.assert_called_once()
    
    @patch('app.Docx2txtLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_docx_with_error(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling of DOCX loading errors."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.docx"
        mock_file.size = 2048
        mock_file.read.return_value = b"fake docx content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.docx"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock DOCX loader to raise exception
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("DOCX loading error")
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 0
        mock_unlink.assert_called_once()
    
    @patch('app.TextLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_load_txt_with_error(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling of TXT loading errors."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.txt"
        mock_file.size = 512
        mock_file.read.return_value = b"fake txt content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.txt"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock TXT loader to raise exception
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("TXT loading error")
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 0
        mock_unlink.assert_called_once()
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_file_cleanup_on_error(self, mock_unlink, mock_tempfile, mock_loader):
        """Test that temporary files are cleaned up even on error."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader to raise exception
        mock_loader_instance = Mock()
        mock_loader_instance.load.side_effect = Exception("Loading error")
        mock_loader.return_value = mock_loader_instance
        
        # Execute
        result = load_documents([mock_file])
        
        # Assertions - file should be cleaned up even on error
        assert len(result) == 0
        mock_unlink.assert_called_once_with("/tmp/test.pdf")
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_file_cleanup_failure_handling(self, mock_unlink, mock_tempfile, mock_loader):
        """Test handling when file cleanup fails."""
        from app import load_documents
        
        # Mock uploaded file
        mock_file = Mock()
        mock_file.name = "test.pdf"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.pdf"
        mock_tmp.__enter__ = Mock(return_value=mock_tmp)
        mock_tmp.__exit__ = Mock(return_value=None)
        mock_tempfile.return_value = mock_tmp
        
        # Mock PDF loader
        mock_doc = Document(page_content="Test content", metadata={"page": 0})
        mock_loader_instance = Mock()
        mock_loader_instance.load.return_value = [mock_doc]
        mock_loader.return_value = mock_loader_instance
        
        # Mock unlink to raise exception
        mock_unlink.side_effect = OSError("Cannot delete file")
        
        # Execute - should not raise exception, just log warning
        result = load_documents([mock_file])
        
        # Assertions
        assert len(result) == 1
        mock_unlink.assert_called_once()
    
    def test_load_empty_file_list(self):
        """Test loading with empty file list."""
        from app import load_documents
        
        result = load_documents([])
        assert len(result) == 0
    
    @patch('app.PyPDFLoader')
    @patch('app.tempfile.NamedTemporaryFile')
    @patch('app.os.unlink')
    def test_file_extension_case_insensitive(self, mock_unlink, mock_tempfile, mock_loader):
        """Test that file extension matching is case insensitive."""
        from app import load_documents
        
        # Mock uploaded file with uppercase extension
        mock_file = Mock()
        mock_file.name = "test.PDF"
        mock_file.size = 1024
        mock_file.read.return_value = b"fake pdf content"
        
        # Mock temporary file
        mock_tmp = Mock()
        mock_tmp.name = "/tmp/test.PDF"
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
        
        # Assertions
        assert len(result) == 1
        assert result[0].metadata['source_file'] == "test.PDF"
        mock_loader.assert_called_once()

