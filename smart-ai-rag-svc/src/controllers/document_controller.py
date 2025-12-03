"""
Document Controller - Handles Document Upload and Management Endpoints.

This controller processes HTTP requests related to document operations including:
- File uploads (PDF files)
- Document indexing by file path
- Input validation and error handling

The controller acts as a bridge between HTTP requests and the RAG service layer,
ensuring proper request validation and response formatting.

Classes:
    DocumentController: Main controller class for document operations.

Example:
    ```python
    controller = DocumentController(rag_service)
    response = await controller.upload_file(uploaded_file)
    ```
"""
import logging
import tempfile
import os
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse

from ..models.schemas import DocumentUploadRequest, DocumentUploadResponse
from ..services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/documents",
    tags=["documents"],
    responses={404: {"description": "Not found"}},
)


class DocumentController:
    """Controller for document-related endpoints."""
    
    def __init__(self, rag_service: EnhancedRAGService):
        """
        Initialize document controller.
        
        Args:
            rag_service: RAG service instance
        """
        self.rag_service = rag_service
        logger.info("DocumentController initialized")
    
    async def upload_file(
        self,
        file: UploadFile,
        use_llamaindex: bool = True
    ) -> DocumentUploadResponse:
        """
        Handle file upload endpoint for PDF documents.
        
        This method processes uploaded PDF files by:
        1. Validating file type (must be PDF)
        2. Saving to temporary file
        3. Processing through RAG service
        4. Cleaning up temporary file
        5. Returning processing results
        
        Args:
            file: FastAPI UploadFile object containing the PDF file.
            use_llamaindex: If True, uses LlamaIndex processor (recommended).
                          If False, uses LangChain processor (legacy).
            
        Returns:
            DocumentUploadResponse containing:
            - success: Whether upload succeeded
            - message: Status message
            - document_stats: Statistics about processed documents
            - original_filename: Name of uploaded file
            
        Raises:
            HTTPException (400): If file is not a PDF or validation fails.
            HTTPException (500): If document processing fails.
            
        Note:
            Temporary files are automatically cleaned up even if processing fails.
            Maximum file size should be enforced at API gateway level.
        """
        try:
            # Validate file type
            if not file.filename.lower().endswith('.pdf'):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Only PDF files are supported"
                )
            
            # Validate file size (optional - can add size limit check here)
            logger.info(f"Processing uploaded file: {file.filename} (LlamaIndex: {use_llamaindex})")
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
                # Read and write file content
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process document through service
                result = self.rag_service.load_and_index_documents(
                    file_path=temp_file_path,
                    use_llamaindex=use_llamaindex,
                    original_filename=file.filename
                )
                
                if not result["success"]:
                    raise HTTPException(
                        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail=result["message"]
                    )
                
                # Enrich response with metadata
                result["original_filename"] = file.filename
                result["processor_used"] = "llamaindex" if use_llamaindex else "langchain"
                
                logger.info(f"Successfully processed file: {file.filename}")
                return DocumentUploadResponse(**result)
                
            finally:
                # Clean up temporary file
                if os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"File upload failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload file: {str(e)}"
            )
    
    async def upload_by_path(
        self,
        request: DocumentUploadRequest,
        use_llamaindex: bool = True
    ) -> DocumentUploadResponse:
        """
        Handle document upload by file path.
        
        Args:
            request: Upload request with file/directory path
            use_llamaindex: Whether to use LlamaIndex for processing
            
        Returns:
            DocumentUploadResponse with upload results
            
        Raises:
            HTTPException: If validation or processing fails
        """
        try:
            # Validate request
            if not request.file_path and not request.directory_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Either file_path or directory_path must be provided"
                )
            
            if request.file_path and request.directory_path:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Provide either file_path or directory_path, not both"
                )
            
            logger.info(f"Processing document upload request (LlamaIndex: {use_llamaindex})")
            
            # Process through service
            result = self.rag_service.load_and_index_documents(
                file_path=request.file_path,
                directory_path=request.directory_path,
                use_llamaindex=use_llamaindex
            )
            
            if not result["success"]:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=result["message"]
                )
            
            result["processor_used"] = "llamaindex" if use_llamaindex else "langchain"
            return DocumentUploadResponse(**result)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Document upload failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload documents: {str(e)}"
            )


# API endpoint functions (to be registered with FastAPI app)
_controller: Optional[DocumentController] = None


def init_controller(rag_service: EnhancedRAGService):
    """Initialize controller with dependencies."""
    global _controller
    _controller = DocumentController(rag_service)


@router.post("/upload-file", response_model=DocumentUploadResponse)
async def upload_file_endpoint(
    file: UploadFile = File(...),
    use_llamaindex: bool = True
):
    """
    Upload and index a PDF file directly.
    
    Args:
        file: PDF file to upload
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False)
    """
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.upload_file(file, use_llamaindex)


@router.post("/upload-path", response_model=DocumentUploadResponse)
async def upload_by_path_endpoint(
    request: DocumentUploadRequest,
    use_llamaindex: bool = True
):
    """
    Upload and index documents by file path.
    
    Args:
        request: Document upload request
        use_llamaindex: Whether to use LlamaIndex (True) or LangChain (False)
    """
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.upload_by_path(request, use_llamaindex)

