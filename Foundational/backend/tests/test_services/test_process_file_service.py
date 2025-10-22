"""Tests for file processing service."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from io import BytesIO


class TestProcessFileService:
    """Test cases for file processing service."""
    
    @pytest.mark.asyncio
    async def test_process_pdf_success(self, sample_pdf_file, mock_mongodb, mock_embeddings):
        """Test successful PDF processing."""
        from src.services.process_file_service import ProcessFileService
        
        service = ProcessFileService()
        
        # Create a file-like object
        file_obj = BytesIO(sample_pdf_file)
        file_obj.name = "test.pdf"
        
        with patch('PyPDF2.PdfReader') as mock_reader:
            mock_page = Mock()
            mock_page.extract_text.return_value = "Test PDF content"
            mock_reader.return_value.pages = [mock_page]
            
            result = await service.process_file(file_obj, "test.pdf")
            
            assert result is not None
            assert "file_id" in result
    
    @pytest.mark.asyncio
    async def test_process_invalid_file(self, mock_mongodb):
        """Test processing invalid file."""
        from src.services.process_file_service import ProcessFileService
        
        service = ProcessFileService()
        
        # Create invalid file
        invalid_file = BytesIO(b"Not a PDF")
        invalid_file.name = "test.txt"
        
        with pytest.raises(ValueError):
            await service.process_file(invalid_file, "test.txt")
    
    @pytest.mark.asyncio
    async def test_get_files(self, mock_mongodb):
        """Test retrieving file list."""
        from src.services.process_file_service import ProcessFileService
        
        service = ProcessFileService()
        mock_mongodb['files'].find.return_value = [
            {"file_id": "file_1", "filename": "doc1.pdf"},
            {"file_id": "file_2", "filename": "doc2.pdf"}
        ]
        
        files = await service.get_files()
        assert isinstance(files, list)
    
    @pytest.mark.asyncio
    async def test_delete_file(self, mock_mongodb):
        """Test file deletion."""
        from src.services.process_file_service import ProcessFileService
        
        service = ProcessFileService()
        result = await service.delete_file(file_id="test_file_123")
        
        assert result is not None

