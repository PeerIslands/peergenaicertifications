"""
Health Controller - Handles health check and monitoring endpoints.

This controller provides health status, service statistics,
and monitoring endpoints for the application.
"""
import logging
from typing import Optional
from datetime import datetime

from fastapi import APIRouter, HTTPException, status

from ..models.schemas import HealthCheckResponse, ServiceStatsResponse
from ..services.enhanced_rag_service import EnhancedRAGService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    tags=["health"],
    responses={404: {"description": "Not found"}},
)


class HealthController:
    """Controller for health and monitoring endpoints."""
    
    def __init__(self, rag_service: Optional[EnhancedRAGService] = None):
        """
        Initialize health controller.
        
        Args:
            rag_service: RAG service instance (optional for basic health checks)
        """
        self.rag_service = rag_service
        logger.info("HealthController initialized")
    
    async def health_check(self) -> HealthCheckResponse:
        """
        Basic health check endpoint.
        
        Returns:
            HealthCheckResponse with service status
        """
        try:
            return HealthCheckResponse(
                status="healthy",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            logger.error(f"Health check failed: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Service unhealthy"
            )
    
    async def root(self) -> HealthCheckResponse:
        """
        Root endpoint with basic service information.
        
        Returns:
            HealthCheckResponse
        """
        return HealthCheckResponse(
            status="healthy",
            timestamp=datetime.now().isoformat()
        )
    
    async def get_stats(self) -> ServiceStatsResponse:
        """
        Get service statistics and configuration.
        
        Returns:
            ServiceStatsResponse with service stats
            
        Raises:
            HTTPException: If stats retrieval fails or service not initialized
        """
        if self.rag_service is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="RAG service not initialized"
            )
        
        try:
            stats = self.rag_service.get_service_stats()
            
            if "error" in stats:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=stats["error"]
                )
            
            logger.info("Successfully retrieved service stats")
            return ServiceStatsResponse(**stats)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Failed to get service stats: {str(e)}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get service stats: {str(e)}"
            )


# API endpoint functions
_controller: Optional[HealthController] = None


def init_controller(rag_service: Optional[EnhancedRAGService] = None):
    """Initialize controller with dependencies."""
    global _controller
    _controller = HealthController(rag_service)


@router.get("/", response_model=HealthCheckResponse)
async def root_endpoint():
    """Root endpoint with basic service information."""
    if _controller is None:
        _controller = HealthController()
    return await _controller.root()


@router.get("/health", response_model=HealthCheckResponse)
async def health_check_endpoint():
    """Health check endpoint."""
    if _controller is None:
        init_controller()
    return await _controller.health_check()


@router.get("/stats", response_model=ServiceStatsResponse)
async def get_stats_endpoint():
    """Get service statistics and configuration."""
    if _controller is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Controller not initialized"
        )
    return await _controller.get_stats()

