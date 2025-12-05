"""
Unit tests for tracing module.
Tests OpenTelemetry distributed tracing functionality.
"""
import pytest
from unittest.mock import patch, MagicMock, Mock
import os

from src.utils.tracing import (
    setup_tracing,
    get_tracer,
    instrument_fastapi,
    trace_function,
    add_span_attributes,
    add_span_event,
    TracingContext
)


class TestTracingSetup:
    """Test tracing setup functionality."""
    
    def test_setup_tracing_basic(self):
        """Test basic tracing setup."""
        tracer = setup_tracing(
            service_name="test-service",
            service_version="1.0.0"
        )
        
        assert tracer is not None
        
    def test_setup_tracing_with_otlp_endpoint(self):
        """Test tracing setup with OTLP endpoint."""
        with patch('src.utils.tracing.OTLPSpanExporter') as mock_exporter:
            tracer = setup_tracing(
                service_name="test-service",
                service_version="1.0.0",
                otlp_endpoint="http://jaeger:4317"
            )
            
            # Verify OTLP exporter was created
            mock_exporter.assert_called_once()
            assert tracer is not None
            
    def test_setup_tracing_with_console_export(self):
        """Test tracing setup with console export enabled."""
        with patch('src.utils.tracing.ConsoleSpanExporter') as mock_console:
            tracer = setup_tracing(
                service_name="test-service",
                enable_console_export=True
            )
            
            mock_console.assert_called_once()
            assert tracer is not None
            
    def test_setup_tracing_with_environment(self):
        """Test tracing setup with environment variable."""
        with patch.dict(os.environ, {'ENVIRONMENT': 'production'}):
            tracer = setup_tracing(service_name="test-service")
            assert tracer is not None
            
    def test_get_tracer(self):
        """Test getting tracer instance."""
        tracer = get_tracer()
        assert tracer is not None
        
        # Get again should return same instance
        tracer2 = get_tracer()
        assert tracer == tracer2


class TestFastAPIInstrumentation:
    """Test FastAPI instrumentation."""
    
    def test_instrument_fastapi(self):
        """Test instrumenting FastAPI app."""
        mock_app = MagicMock()
        
        with patch('src.utils.tracing.FastAPIInstrumentor') as mock_instrumentor_class:
            # Mock the class method instrument_app
            mock_instrumentor_class.instrument_app = MagicMock()
            
            instrument_fastapi(mock_app)
            
            # Verify instrumentation was called
            mock_instrumentor_class.instrument_app.assert_called_once_with(mock_app)


class TestTraceFunctionDecorator:
    """Test trace_function decorator."""
    
    def test_trace_function_basic(self):
        """Test basic function tracing."""
        
        @trace_function()
        def test_func():
            return "test result"
        
        result = test_func()
        assert result == "test result"
        
    def test_trace_function_with_span_name(self):
        """Test tracing with custom span name."""
        
        @trace_function(span_name="custom_operation")
        def test_func():
            return "test"
        
        result = test_func()
        assert result == "test"
        
    def test_trace_function_with_attributes(self):
        """Test tracing with custom attributes."""
        
        @trace_function(span_name="test_op", attributes={"key": "value"})
        def test_func():
            return "test"
        
        result = test_func()
        assert result == "test"
        
    def test_trace_function_with_exception(self):
        """Test tracing function that raises exception."""
        
        @trace_function()
        def failing_func():
            raise ValueError("Test error")
        
        with pytest.raises(ValueError, match="Test error"):
            failing_func()
            
    def test_trace_async_function(self):
        """Test tracing async function."""
        import asyncio
        
        @trace_function(span_name="async_operation")
        async def async_func():
            await asyncio.sleep(0.01)
            return "async result"
        
        result = asyncio.run(async_func())
        assert result == "async result"
        
    def test_trace_async_function_with_exception(self):
        """Test tracing async function that raises exception."""
        import asyncio
        
        @trace_function()
        async def failing_async_func():
            await asyncio.sleep(0.01)
            raise RuntimeError("Async error")
        
        with pytest.raises(RuntimeError, match="Async error"):
            asyncio.run(failing_async_func())


class TestSpanAttributes:
    """Test adding span attributes."""
    
    def test_add_span_attributes(self):
        """Test adding attributes to current span."""
        # This should not raise an error even without active span
        add_span_attributes(key1="value1", key2="value2")
        assert True
        
    def test_add_span_attributes_with_different_types(self):
        """Test adding attributes of different types."""
        add_span_attributes(
            string_attr="text",
            int_attr=42,
            float_attr=3.14,
            bool_attr=True
        )
        assert True


class TestSpanEvents:
    """Test adding span events."""
    
    def test_add_span_event_basic(self):
        """Test adding basic span event."""
        add_span_event("test_event")
        assert True
        
    def test_add_span_event_with_attributes(self):
        """Test adding span event with attributes."""
        add_span_event(
            "operation_complete",
            attributes={"status": "success", "items": 10}
        )
        assert True


class TestTracingContext:
    """Test TracingContext context manager."""
    
    def test_tracing_context_basic(self):
        """Test basic tracing context."""
        with TracingContext("test_operation"):
            pass
        
        assert True
        
    def test_tracing_context_with_attributes(self):
        """Test tracing context with attributes."""
        with TracingContext("test_operation", {"key": "value"}):
            pass
        
        assert True
        
    def test_tracing_context_with_exception(self):
        """Test tracing context with exception."""
        with pytest.raises(ValueError):
            with TracingContext("failing_operation"):
                raise ValueError("Test error")
                
    def test_tracing_context_returns_span(self):
        """Test that tracing context returns span."""
        with TracingContext("test_operation") as span:
            # Span should be available
            assert span is not None


class TestTracingIntegration:
    """Integration tests for tracing."""
    
    def test_complete_tracing_flow(self):
        """Test complete tracing flow."""
        # Setup tracing
        tracer = setup_tracing(service_name="integration-test")
        
        # Use decorator
        @trace_function(span_name="integration_test")
        def test_operation():
            add_span_attributes(step="1", status="processing")
            add_span_event("processing_started")
            return "complete"
        
        result = test_operation()
        assert result == "complete"
        
    def test_nested_tracing(self):
        """Test nested tracing operations."""
        
        @trace_function(span_name="outer_operation")
        def outer_func():
            with TracingContext("inner_operation"):
                add_span_attributes(level="inner")
            return "done"
        
        result = outer_func()
        assert result == "done"
        
    def test_tracing_with_metrics_simulation(self):
        """Test tracing combined with metrics (simulated)."""
        import time
        
        @trace_function(span_name="measured_operation")
        def measured_func():
            start = time.time()
            time.sleep(0.01)
            duration = time.time() - start
            add_span_attributes(duration_seconds=duration)
            return duration
        
        duration = measured_func()
        assert duration > 0


class TestTracingErrorHandling:
    """Test error handling in tracing."""
    
    def test_tracing_without_setup(self):
        """Test that tracing works even without explicit setup."""
        # get_tracer should initialize if not already done
        tracer = get_tracer()
        assert tracer is not None
        
    def test_add_attributes_without_span(self):
        """Test adding attributes when no span is active."""
        # Should not raise error
        add_span_attributes(key="value")
        assert True
        
    def test_add_event_without_span(self):
        """Test adding event when no span is active."""
        # Should not raise error
        add_span_event("test_event")
        assert True


class TestTracingConfiguration:
    """Test tracing configuration options."""
    
    def test_different_service_names(self):
        """Test tracing with different service names."""
        tracer1 = setup_tracing(service_name="service1", service_version="1.0")
        tracer2 = setup_tracing(service_name="service2", service_version="2.0")
        
        # Both should be valid tracers
        assert tracer1 is not None
        assert tracer2 is not None
        
    def test_tracing_with_all_options(self):
        """Test tracing setup with all options enabled."""
        with patch('src.utils.tracing.OTLPSpanExporter') as mock_otlp:
            with patch('src.utils.tracing.ConsoleSpanExporter') as mock_console:
                tracer = setup_tracing(
                    service_name="full-test",
                    service_version="1.0.0",
                    otlp_endpoint="http://localhost:4317",
                    enable_console_export=True
                )
                
                assert tracer is not None
                mock_otlp.assert_called_once()
                mock_console.assert_called_once()
