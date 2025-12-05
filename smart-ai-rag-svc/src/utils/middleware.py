"""
Custom middleware for the Smart AI RAG Service.
Handles request tracking, correlation IDs, and observability.
"""
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import time
import uuid
from typing import Callable

from .logging_config import set_request_context, clear_request_context, get_logger
from .metrics import http_requests_total, http_request_duration_seconds, active_requests, track_error
from .tracing import add_span_attributes

logger = get_logger(__name__)


class ObservabilityMiddleware(BaseHTTPMiddleware):
    """
    Middleware for observability: logging, metrics, and tracing.
    """
    
    def __init__(self, app: ASGIApp):
        """Initialize middleware."""
        super().__init__(app)
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request with observability tracking.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
        
        Returns:
            Response
        """
        # Generate or extract request ID
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        
        # Set request context for logging
        set_request_context(request_id)
        
        # Track active requests
        active_requests.inc()
        start_time = time.time()
        
        # Add tracing attributes
        add_span_attributes(
            request_id=request_id,
            http_method=request.method,
            http_url=str(request.url),
            http_path=request.url.path
        )
        
        # Log request start
        logger.info(
            f"{request.method} {request.url.path}",
            method=request.method,
            path=request.url.path,
            request_id=request_id,
            client_host=request.client.host if request.client else None
        )
        
        # Process request
        response = None
        status_code = 500
        
        try:
            response = await call_next(request)
            status_code = response.status_code
            
            # Add request ID to response headers
            response.headers['X-Request-ID'] = request_id
            
            return response
            
        except Exception as e:
            # Track error
            track_error(
                error_type=type(e).__name__,
                component='api'
            )
            
            logger.error(
                f"Request failed: {str(e)}",
                method=request.method,
                path=request.url.path,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
            
        finally:
            # Calculate duration
            duration = time.time() - start_time
            
            # Record metrics
            http_requests_total.labels(
                method=request.method,
                endpoint=request.url.path,
                status=status_code
            ).inc()
            
            http_request_duration_seconds.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            active_requests.dec()
            
            # Log request completion
            logger.info(
                f"{request.method} {request.url.path} - {status_code}",
                method=request.method,
                path=request.url.path,
                status_code=status_code,
                duration_seconds=round(duration, 3),
                request_id=request_id
            )
            
            # Clear request context
            clear_request_context()


class CORSSecurityHeaders(BaseHTTPMiddleware):
    """
    Middleware to add security headers to responses.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)
        
        # Add security headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response

