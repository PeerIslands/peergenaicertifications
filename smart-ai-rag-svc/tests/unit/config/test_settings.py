"""
Unit tests for settings configuration.
"""
import pytest
from unittest.mock import patch


class TestSettings:
    """Test settings configuration."""
    
    def test_settings_loaded(self, mock_env_vars):
        """Test that settings are loaded correctly."""
        # Reload settings after env vars are set
        import importlib
        from src.config import settings as settings_module
        importlib.reload(settings_module)
        
        assert settings_module.settings.openai_api_key is not None
        assert settings_module.settings.mongodb_uri is not None
        assert settings_module.settings.chunk_size == 1000
        assert settings_module.settings.chunk_overlap == 200
    
    def test_settings_defaults(self, mock_env_vars, monkeypatch):
        """Test default values."""
        monkeypatch.delenv("CHUNK_SIZE", raising=False)
        
        # Re-import to get new settings
        import importlib
        from src.config import settings as settings_module
        importlib.reload(settings_module)
        
        assert settings_module.settings.chunk_size == 1000  # Default
    
    def test_settings_type_casting(self, mock_env_vars):
        """Test that settings are properly type casted."""
        from src.config.settings import settings
        
        assert isinstance(settings.chunk_size, int)
        assert isinstance(settings.temperature, float)
        assert isinstance(settings.max_tokens, int)

