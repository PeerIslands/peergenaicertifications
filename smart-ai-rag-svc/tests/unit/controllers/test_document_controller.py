"""
Unit tests for DocumentController.
"""
import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from fastapi import UploadFile, HTTPException
import io

from src.controllers.document_controller import DocumentController
from src.models.schemas import DocumentUploadRequest


class TestDocumentController:
    """Test DocumentController class."""
    
    @pytest.fixture
    def controller(self, mock_rag_service):
        """Create DocumentController instance."""
        return DocumentController(mock_rag_service)
    
    @pytest.mark.asyncio
    async def test_upload_file_success(self, controller, mock_rag_service):
        """Test successful file upload."""
        # Create mock file
        file_content = b"%PDF-1.4\nTest PDF content"
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.pdf"
        mock_file.read = AsyncMock(return_value=file_content)
        
        # Execute
        result = await controller.upload_file(mock_file, use_llamaindex=True)
        
        # Verify
        assert result.success is True
        assert result.message == "Documents indexed successfully"
        assert mock_rag_service.load_and_index_documents.called
    
    @pytest.mark.asyncio
    async def test_upload_file_invalid_extension(self, controller):
        """Test upload with invalid file extension."""
        mock_file = MagicMock(spec=UploadFile)
        mock_file.filename = "test.txt"
        
        with pytest.raises(HTTPException) as exc:
            await controller.upload_file(mock_file)
        
        assert exc.value.status_code == 400
        assert "PDF" in str(exc.value.detail)
    
    @pytest.mark.asyncio
    async def test_upload_by_path_success(self, controller, mock_rag_service):
        """Test upload by file path."""
        request = DocumentUploadRequest(file_path="/path/to/file.pdf")
        
        result = await controller.upload_by_path(request, use_llamaindex=True)
        
        assert result.success is True
        assert mock_rag_service.load_and_index_documents.called
    
    @pytest.mark.asyncio
    async def test_upload_by_path_no_path_provided(self, controller):
        """Test upload without file or directory path."""
        request = DocumentUploadRequest()
        
        with pytest.raises(HTTPException) as exc:
            await controller.upload_by_path(request)
        
        assert exc.value.status_code == 400
    
    @pytest.mark.asyncio
    async def test_upload_by_path_both_paths_provided(self, controller):
        """Test upload with both file and directory path."""
        request = DocumentUploadRequest(
            file_path="/path/to/file.pdf",
            directory_path="/path/to/dir"
        )
        
        with pytest.raises(HTTPException) as exc:
            await controller.upload_by_path(request)
        
        assert exc.value.status_code == 400

