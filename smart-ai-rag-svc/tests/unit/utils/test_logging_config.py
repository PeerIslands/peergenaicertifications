"""
Unit tests for logging configuration module.
Tests structured logging, JSON formatting, and context management.
"""
import pytest
import json
import logging
from datetime import datetime
from unittest.mock import patch, MagicMock

from src.utils.logging_config import (
    JSONFormatter,
    StructuredLogger,
    setup_logging,
    get_logger,
    set_request_context,
    clear_request_context,
    request_id_var,
    user_id_var
)


class TestJSONFormatter:
    """Test JSONFormatter class."""
    
    def test_json_formatter_basic_log(self):
        """Test basic JSON log formatting."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test message",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        log_data = json.loads(output)
        
        assert log_data["level"] == "INFO"
        assert log_data["logger"] == "test.logger"
        assert log_data["message"] == "Test message"
        assert log_data["line"] == 42
        assert "timestamp" in log_data
        
    def test_json_formatter_with_request_id(self):
        """Test JSON formatter includes request ID from context."""
        formatter = JSONFormatter()
        request_id_var.set("test-request-id-123")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test with request ID",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        log_data = json.loads(output)
        
        assert log_data["request_id"] == "test-request-id-123"
        
        # Cleanup
        request_id_var.set(None)
        
    def test_json_formatter_with_user_id(self):
        """Test JSON formatter includes user ID from context."""
        formatter = JSONFormatter()
        user_id_var.set("user-456")
        
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test with user ID",
            args=(),
            exc_info=None
        )
        
        output = formatter.format(record)
        log_data = json.loads(output)
        
        assert log_data["user_id"] == "user-456"
        
        # Cleanup
        user_id_var.set(None)
        
    def test_json_formatter_with_exception(self):
        """Test JSON formatter includes exception information."""
        import sys
        formatter = JSONFormatter()
        
        try:
            raise ValueError("Test error")
        except ValueError:
            exc_info = sys.exc_info()
            record = logging.LogRecord(
                name="test.logger",
                level=logging.ERROR,
                pathname="/path/to/file.py",
                lineno=42,
                msg="Error occurred",
                args=(),
                exc_info=exc_info
            )
            
            output = formatter.format(record)
            log_data = json.loads(output)
            
            assert "exception" in log_data
            assert "ValueError: Test error" in log_data["exception"]
    
    def test_json_formatter_with_extra_fields(self):
        """Test JSON formatter includes extra fields."""
        formatter = JSONFormatter()
        record = logging.LogRecord(
            name="test.logger",
            level=logging.INFO,
            pathname="/path/to/file.py",
            lineno=42,
            msg="Test with extras",
            args=(),
            exc_info=None
        )
        record.extra_fields = {"document_id": "doc-123", "pages": 10}
        
        output = formatter.format(record)
        log_data = json.loads(output)
        
        assert log_data["document_id"] == "doc-123"
        assert log_data["pages"] == 10


class TestStructuredLogger:
    """Test StructuredLogger class."""
    
    def test_structured_logger_creation(self):
        """Test creating a structured logger."""
        logger = StructuredLogger("test.logger")
        assert logger.logger.name == "test.logger"
        
    def test_debug_logging(self):
        """Test debug level logging."""
        logger = StructuredLogger("test.logger")
        with patch.object(logger.logger, 'log') as mock_log:
            logger.debug("Debug message", key="value")
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][0] == logging.DEBUG
            assert args[0][1] == "Debug message"
            
    def test_info_logging(self):
        """Test info level logging."""
        logger = StructuredLogger("test.logger")
        with patch.object(logger.logger, 'log') as mock_log:
            logger.info("Info message", key="value")
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][0] == logging.INFO
            
    def test_warning_logging(self):
        """Test warning level logging."""
        logger = StructuredLogger("test.logger")
        with patch.object(logger.logger, 'log') as mock_log:
            logger.warning("Warning message", key="value")
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][0] == logging.WARNING
            
    def test_error_logging(self):
        """Test error level logging."""
        logger = StructuredLogger("test.logger")
        with patch.object(logger.logger, 'log') as mock_log:
            logger.error("Error message", key="value")
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][0] == logging.ERROR
            
    def test_critical_logging(self):
        """Test critical level logging."""
        logger = StructuredLogger("test.logger")
        with patch.object(logger.logger, 'log') as mock_log:
            logger.critical("Critical message", key="value")
            mock_log.assert_called_once()
            args = mock_log.call_args
            assert args[0][0] == logging.CRITICAL


class TestLoggingSetup:
    """Test logging setup functions."""
    
    def test_setup_logging_with_json(self):
        """Test setting up logging with JSON formatter."""
        setup_logging(log_level="INFO", use_json=True)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO
        assert len(root_logger.handlers) > 0
        
        # Check if JSON formatter is used
        handler = root_logger.handlers[0]
        assert isinstance(handler.formatter, JSONFormatter)
        
    def test_setup_logging_without_json(self):
        """Test setting up logging with standard formatter."""
        setup_logging(log_level="DEBUG", use_json=False)
        
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG
        assert len(root_logger.handlers) > 0
        
        # Check if standard formatter is used
        handler = root_logger.handlers[0]
        assert not isinstance(handler.formatter, JSONFormatter)
        
    def test_get_logger(self):
        """Test getting a structured logger."""
        logger = get_logger("test.module")
        assert isinstance(logger, StructuredLogger)
        assert logger.logger.name == "test.module"


class TestContextManagement:
    """Test request context management."""
    
    def test_set_request_context(self):
        """Test setting request context."""
        set_request_context("request-123", "user-456")
        
        assert request_id_var.get() == "request-123"
        assert user_id_var.get() == "user-456"
        
        # Cleanup
        clear_request_context()
        
    def test_set_request_context_without_user(self):
        """Test setting request context without user ID."""
        set_request_context("request-789")
        
        assert request_id_var.get() == "request-789"
        assert user_id_var.get() is None
        
        # Cleanup
        clear_request_context()
        
    def test_clear_request_context(self):
        """Test clearing request context."""
        set_request_context("request-123", "user-456")
        clear_request_context()
        
        assert request_id_var.get() is None
        assert user_id_var.get() is None
        
    def test_context_isolation(self):
        """Test that context is isolated between calls."""
        # Set context
        set_request_context("request-1", "user-1")
        assert request_id_var.get() == "request-1"
        
        # Clear and set new context
        clear_request_context()
        set_request_context("request-2", "user-2")
        
        assert request_id_var.get() == "request-2"
        assert user_id_var.get() == "user-2"
        
        # Cleanup
        clear_request_context()


class TestLoggingIntegration:
    """Integration tests for logging functionality."""
    
    def test_end_to_end_logging_with_context(self):
        """Test complete logging flow with context."""
        setup_logging(log_level="INFO", use_json=True)
        logger = get_logger("integration.test")
        
        # Set context
        set_request_context("integration-request-123", "integration-user-456")
        
        # Log a message (we can't easily capture the output, but we can verify it doesn't crash)
        logger.info("Integration test message", operation="test", status="success")
        
        # Cleanup
        clear_request_context()
        
    def test_logging_different_levels(self):
        """Test logging at different levels."""
        setup_logging(log_level="DEBUG", use_json=False)
        logger = get_logger("level.test")
        
        # These should all work without errors
        logger.debug("Debug level")
        logger.info("Info level")
        logger.warning("Warning level")
        logger.error("Error level")
        logger.critical("Critical level")
