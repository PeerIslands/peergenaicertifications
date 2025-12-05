"""
OpenTelemetry distributed tracing for the Smart AI RAG Service.
Provides end-to-end request tracing and performance insights.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.instrumentation.pymongo import PymongoInstrumentor
from typing import Optional, Dict, Any
from functools import wraps
import os

# Global tracer
_tracer: Optional[trace.Tracer] = None


def setup_tracing(
    service_name: str = "smart-ai-rag-service",
    service_version: str = "2.0.0",
    otlp_endpoint: Optional[str] = None,
    enable_console_export: bool = False
) -> trace.Tracer:
    """
    Setup OpenTelemetry tracing.
    
    Args:
        service_name: Name of the service
        service_version: Version of the service
        otlp_endpoint: OTLP collector endpoint (e.g., 'http://localhost:4317')
        enable_console_export: If True, also export to console
    
    Returns:
        Configured tracer instance
    """
    global _tracer
    
    # Create resource
    resource = Resource(attributes={
        SERVICE_NAME: service_name,
        SERVICE_VERSION: service_version,
        "deployment.environment": os.getenv("ENVIRONMENT", "development")
    })
    
    # Create tracer provider
    provider = TracerProvider(resource=resource)
    
    # Add OTLP exporter if endpoint provided
    if otlp_endpoint:
        otlp_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
        provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    
    # Add console exporter if enabled (useful for development)
    if enable_console_export:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))
    
    # Set as global tracer provider
    trace.set_tracer_provider(provider)
    
    # Get tracer
    _tracer = trace.get_tracer(__name__)
    
    # Auto-instrument libraries
    HTTPXClientInstrumentor().instrument()
    PymongoInstrumentor().instrument()
    
    return _tracer


def get_tracer() -> trace.Tracer:
    """
    Get the global tracer instance.
    
    Returns:
        Tracer instance
    """
    global _tracer
    if _tracer is None:
        _tracer = setup_tracing()
    return _tracer


def instrument_fastapi(app):
    """
    Instrument FastAPI app with tracing.
    
    Args:
        app: FastAPI application instance
    """
    FastAPIInstrumentor.instrument_app(app)


def trace_function(span_name: Optional[str] = None, attributes: Optional[Dict[str, Any]] = None):
    """
    Decorator to trace function execution.
    
    Args:
        span_name: Optional custom span name (defaults to function name)
        attributes: Optional attributes to add to the span
    
    Example:
        @trace_function(span_name="process_document", attributes={"framework": "langchain"})
        def process_document(doc):
            ...
    """
    def decorator(func):
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = get_tracer()
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                
                # Add function arguments as attributes (be careful with sensitive data)
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = func(*args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = get_tracer()
            name = span_name or f"{func.__module__}.{func.__name__}"
            
            with tracer.start_as_current_span(name) as span:
                # Add custom attributes
                if attributes:
                    for key, value in attributes.items():
                        span.set_attribute(key, str(value))
                
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)
                
                try:
                    result = await func(*args, **kwargs)
                    span.set_attribute("status", "success")
                    return result
                except Exception as e:
                    span.set_attribute("status", "error")
                    span.set_attribute("error.type", type(e).__name__)
                    span.set_attribute("error.message", str(e))
                    span.record_exception(e)
                    raise
        
        # Return appropriate wrapper based on function type
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def add_span_attributes(**attributes):
    """
    Add attributes to the current span.
    
    Args:
        **attributes: Key-value pairs to add as attributes
    """
    span = trace.get_current_span()
    if span:
        for key, value in attributes.items():
            span.set_attribute(key, str(value))


def add_span_event(name: str, attributes: Optional[Dict[str, Any]] = None):
    """
    Add an event to the current span.
    
    Args:
        name: Event name
        attributes: Optional event attributes
    """
    span = trace.get_current_span()
    if span:
        span.add_event(name, attributes=attributes or {})


class TracingContext:
    """Context manager for creating custom spans."""
    
    def __init__(self, span_name: str, attributes: Optional[Dict[str, Any]] = None):
        """
        Initialize tracing context.
        
        Args:
            span_name: Name of the span
            attributes: Optional span attributes
        """
        self.span_name = span_name
        self.attributes = attributes or {}
        self.span = None
    
    def __enter__(self):
        """Enter context."""
        tracer = get_tracer()
        self.span = tracer.start_span(self.span_name)
        
        # Add attributes
        for key, value in self.attributes.items():
            self.span.set_attribute(key, str(value))
        
        return self.span
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        if self.span:
            if exc_type is not None:
                self.span.set_attribute("status", "error")
                self.span.set_attribute("error.type", exc_type.__name__)
                self.span.set_attribute("error.message", str(exc_val))
                self.span.record_exception(exc_val)
            else:
                self.span.set_attribute("status", "success")
            
            self.span.end()

