"""Tests for session service."""
import pytest
from unittest.mock import Mock, patch


class TestSessionService:
    """Test cases for session service."""
    
    def test_create_session(self, mock_mongodb):
        """Test session creation."""
        from src.services.session_service import SessionService
        
        service = SessionService()
        session_id = service.create_session(file_id="test_file_123")
        
        assert session_id is not None
        assert isinstance(session_id, str)
        assert len(session_id) > 0
    
    def test_create_session_without_file(self):
        """Test session creation without file ID."""
        from src.services.session_service import SessionService
        
        service = SessionService()
        
        with pytest.raises(ValueError):
            service.create_session(file_id="")
    
    def test_get_sessions(self, mock_mongodb):
        """Test retrieving all sessions."""
        from src.services.session_service import SessionService
        
        service = SessionService()
        mock_mongodb['sessions'].find.return_value = [
            {"session_id": "session_1", "file_id": "file_1"},
            {"session_id": "session_2", "file_id": "file_2"}
        ]
        
        sessions = service.get_sessions()
        assert isinstance(sessions, list)
    
    def test_delete_session(self, mock_mongodb):
        """Test session deletion."""
        from src.services.session_service import SessionService
        
        service = SessionService()
        result = service.delete_session(session_id="test_session_123")
        
        assert result is not None

