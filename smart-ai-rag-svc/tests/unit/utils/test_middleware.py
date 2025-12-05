"""
Unit tests for middleware module.
Tests ObservabilityMiddleware and CORSSecurityHeaders.
"""
import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
import time

from src.utils.middleware import ObservabilityMiddleware, CORSSecurityHeaders


class TestObservabilityMiddleware:
    """Test ObservabilityMiddleware class."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        return ObservabilityMiddleware(app)
        
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = MagicMock()
        request.url.path = "/test"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        return request
        
    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = MagicMock(spec=Response)
        response.status_code = 200
        response.headers = {}
        return response
    
    @pytest.mark.asyncio
    async def test_middleware_generates_request_id(self, middleware, mock_request, mock_response):
        """Test that middleware generates request ID."""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('src.utils.middleware.set_request_context') as mock_set_context:
            with patch('src.utils.middleware.clear_request_context') as mock_clear_context:
                with patch('src.utils.middleware.active_requests') as mock_active:
                    with patch('src.utils.middleware.http_requests_total') as mock_total:
                        with patch('src.utils.middleware.http_request_duration_seconds') as mock_duration:
                            response = await middleware.dispatch(mock_request, call_next)
                            
                            # Verify request context was set
                            assert mock_set_context.called
                            
                            # Verify response has request ID header
                            assert 'X-Request-ID' in response.headers
                            
                            # Verify context was cleared
                            assert mock_clear_context.called
    
    @pytest.mark.asyncio
    async def test_middleware_uses_existing_request_id(self, middleware, mock_request, mock_response):
        """Test that middleware uses existing X-Request-ID header."""
        mock_request.headers = {'X-Request-ID': 'existing-id-123'}
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('src.utils.middleware.set_request_context') as mock_set_context:
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests'):
                    with patch('src.utils.middleware.http_requests_total'):
                        with patch('src.utils.middleware.http_request_duration_seconds'):
                            response = await middleware.dispatch(mock_request, call_next)
                            
                            # Verify existing ID was used
                            mock_set_context.assert_called_once()
                            call_args = mock_set_context.call_args[0]
                            assert call_args[0] == 'existing-id-123'
    
    @pytest.mark.asyncio
    async def test_middleware_tracks_metrics(self, middleware, mock_request, mock_response):
        """Test that middleware tracks metrics."""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests') as mock_active:
                    with patch('src.utils.middleware.http_requests_total') as mock_total:
                        with patch('src.utils.middleware.http_request_duration_seconds') as mock_duration:
                            # Mock the metrics
                            mock_active.inc = MagicMock()
                            mock_active.dec = MagicMock()
                            mock_total.labels = MagicMock(return_value=MagicMock(inc=MagicMock()))
                            mock_duration.labels = MagicMock(return_value=MagicMock(observe=MagicMock()))
                            
                            await middleware.dispatch(mock_request, call_next)
                            
                            # Verify metrics were called
                            mock_active.inc.assert_called_once()
                            mock_active.dec.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_middleware_handles_exceptions(self, middleware, mock_request):
        """Test that middleware handles exceptions properly."""
        # Mock call_next to raise exception
        call_next = AsyncMock(side_effect=ValueError("Test error"))
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests') as mock_active:
                    with patch('src.utils.middleware.http_requests_total') as mock_total:
                        with patch('src.utils.middleware.http_request_duration_seconds') as mock_duration:
                            with patch('src.utils.middleware.track_error') as mock_track_error:
                                # Mock metrics
                                mock_active.inc = MagicMock()
                                mock_active.dec = MagicMock()
                                mock_total.labels = MagicMock(return_value=MagicMock(inc=MagicMock()))
                                mock_duration.labels = MagicMock(return_value=MagicMock(observe=MagicMock()))
                                
                                with pytest.raises(ValueError, match="Test error"):
                                    await middleware.dispatch(mock_request, call_next)
                                
                                # Verify error was tracked
                                mock_track_error.assert_called_once()
                                
                                # Verify active requests was decremented
                                mock_active.dec.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_middleware_adds_tracing_attributes(self, middleware, mock_request, mock_response):
        """Test that middleware adds tracing attributes."""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests'):
                    with patch('src.utils.middleware.http_requests_total'):
                        with patch('src.utils.middleware.http_request_duration_seconds'):
                            with patch('src.utils.middleware.add_span_attributes') as mock_add_attrs:
                                await middleware.dispatch(mock_request, call_next)
                                
                                # Verify span attributes were added
                                mock_add_attrs.assert_called_once()
                                call_kwargs = mock_add_attrs.call_args[1]
                                assert 'request_id' in call_kwargs
                                assert call_kwargs['http_method'] == 'GET'
                                assert call_kwargs['http_path'] == '/test'
    
    @pytest.mark.asyncio
    async def test_middleware_logs_requests(self, middleware, mock_request, mock_response):
        """Test that middleware logs requests."""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests'):
                    with patch('src.utils.middleware.http_requests_total'):
                        with patch('src.utils.middleware.http_request_duration_seconds'):
                            with patch('src.utils.middleware.logger') as mock_logger:
                                await middleware.dispatch(mock_request, call_next)
                                
                                # Verify logging was called (at least for request start and completion)
                                assert mock_logger.info.call_count >= 2


class TestCORSSecurityHeaders:
    """Test CORSSecurityHeaders middleware."""
    
    @pytest.fixture
    def middleware(self):
        """Create middleware instance."""
        app = MagicMock()
        return CORSSecurityHeaders(app)
        
    @pytest.fixture
    def mock_request(self):
        """Create mock request."""
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = MagicMock()
        request.url.path = "/test"
        return request
        
    @pytest.fixture
    def mock_response(self):
        """Create mock response."""
        response = Response()
        return response
    
    @pytest.mark.asyncio
    async def test_security_headers_added(self, middleware, mock_request, mock_response):
        """Test that security headers are added to response."""
        call_next = AsyncMock(return_value=mock_response)
        
        response = await middleware.dispatch(mock_request, call_next)
        
        # Verify security headers
        assert response.headers['X-Content-Type-Options'] == 'nosniff'
        assert response.headers['X-Frame-Options'] == 'DENY'
        assert response.headers['X-XSS-Protection'] == '1; mode=block'
        assert 'Strict-Transport-Security' in response.headers
        assert 'max-age=31536000' in response.headers['Strict-Transport-Security']
    
    @pytest.mark.asyncio
    async def test_security_headers_all_present(self, middleware, mock_request, mock_response):
        """Test that all expected security headers are present."""
        call_next = AsyncMock(return_value=mock_response)
        
        response = await middleware.dispatch(mock_request, call_next)
        
        # Check all expected headers
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options',
            'X-XSS-Protection',
            'Strict-Transport-Security'
        ]
        
        for header in expected_headers:
            assert header in response.headers, f"Header {header} is missing"
    
    @pytest.mark.asyncio
    async def test_security_headers_preserves_existing_headers(self, middleware, mock_request, mock_response):
        """Test that security headers don't override existing response headers."""
        # Add existing header
        mock_response.headers['X-Custom-Header'] = 'custom-value'
        call_next = AsyncMock(return_value=mock_response)
        
        response = await middleware.dispatch(mock_request, call_next)
        
        # Verify existing header is preserved
        assert response.headers['X-Custom-Header'] == 'custom-value'
        
        # Verify security headers are added
        assert 'X-Content-Type-Options' in response.headers


class TestMiddlewareIntegration:
    """Integration tests for middleware."""
    
    @pytest.mark.asyncio
    async def test_both_middlewares_together(self, mock_request):
        """Test both middlewares working together."""
        app = MagicMock()
        
        # Create response
        mock_response = Response(content="test", status_code=200)
        call_next = AsyncMock(return_value=mock_response)
        
        # Apply observability middleware
        obs_middleware = ObservabilityMiddleware(app)
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests'):
                    with patch('src.utils.middleware.http_requests_total'):
                        with patch('src.utils.middleware.http_request_duration_seconds'):
                            response1 = await obs_middleware.dispatch(mock_request, call_next)
        
        # Apply security headers middleware
        sec_middleware = CORSSecurityHeaders(app)
        call_next2 = AsyncMock(return_value=response1)
        response2 = await sec_middleware.dispatch(mock_request, call_next2)
        
        # Verify both middlewares' effects
        assert 'X-Request-ID' in response2.headers  # From observability
        assert 'X-Content-Type-Options' in response2.headers  # From security
    
    @pytest.fixture
    def mock_request(self):
        """Create mock request for integration tests."""
        request = MagicMock(spec=Request)
        request.method = "POST"
        request.url = MagicMock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "192.168.1.1"
        return request


class TestMiddlewarePerformance:
    """Test middleware performance characteristics."""
    
    @pytest.mark.asyncio
    async def test_middleware_overhead_minimal(self):
        """Test that middleware adds minimal overhead."""
        app = MagicMock()
        middleware = ObservabilityMiddleware(app)
        
        request = MagicMock(spec=Request)
        request.method = "GET"
        request.url = MagicMock()
        request.url.path = "/fast"
        request.headers = {}
        request.client = MagicMock()
        request.client.host = "127.0.0.1"
        
        response = Response()
        call_next = AsyncMock(return_value=response)
        
        with patch('src.utils.middleware.set_request_context'):
            with patch('src.utils.middleware.clear_request_context'):
                with patch('src.utils.middleware.active_requests'):
                    with patch('src.utils.middleware.http_requests_total'):
                        with patch('src.utils.middleware.http_request_duration_seconds'):
                            start_time = time.time()
                            await middleware.dispatch(request, call_next)
                            duration = time.time() - start_time
                            
                            # Middleware overhead should be less than 10ms
                            assert duration < 0.01
