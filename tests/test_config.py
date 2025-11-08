import pytest
import os
from unittest.mock import patch
import config


class TestConfig:

    def test_config_loads_environment_variables(self, mock_env_vars):
        with patch.dict(
            os.environ, {"OPENAI_API_KEY": "test-key", "MONGODB_URI": "mongodb://test"}
        ):
            from importlib import reload

            reload(config)
            assert config.OPENAI_API_KEY == "test-key"
            assert config.MONGODB_URI == "mongodb://test"

    def test_config_has_default_values(self, mock_env_vars):
        assert config.EMBEDDING_MODEL == "all-MiniLM-L6-v2"
        assert config.CHUNK_SIZE == 1000
        assert config.CHUNK_OVERLAP == 200

    def test_mongodb_pool_configuration(self, mock_env_vars):
        assert isinstance(config.MONGODB_POOL_SIZE, int)
        assert isinstance(config.MONGODB_MAX_POOL_SIZE, int)
        assert config.MONGODB_POOL_SIZE <= config.MONGODB_MAX_POOL_SIZE

    def test_setup_logging(self, mock_env_vars):
        logger = config.setup_logging()
        assert logger is not None
        assert logger.name == "config"

    def test_logging_configuration(self, mock_env_vars):
        assert config.LOG_FORMAT is not None
        assert "%(levelname)s" in config.LOG_FORMAT
        assert "%(message)s" in config.LOG_FORMAT
