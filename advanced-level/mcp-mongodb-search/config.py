"""
Configuration file for MCP MongoDB Search Solution
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file FIRST
load_dotenv()


def _load_config():
    """Load configuration values from environment"""
    load_dotenv()  # Ensure .env is loaded
    return {
        'MONGODB_CONNECTION_STRING': os.getenv('MONGODB_CONNECTION_STRING', 'mongodb://localhost:27017'),
        'MONGODB_DATABASE': os.getenv('MONGODB_DATABASE', 'PeerGenAI_practice_db'),
        'AZURE_OPENAI_ENDPOINT': os.getenv('AZURE_OPENAI_ENDPOINT', ''),
        'AZURE_OPENAI_API_KEY': os.getenv('AZURE_OPENAI_API_KEY', ''),
        'AZURE_OPENAI_API_VERSION': os.getenv('AZURE_OPENAI_API_VERSION', '2024-06-01'),
        'AZURE_OPENAI_CHAT_DEPLOYMENT_NAME': os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME', ''),
        'AZURE_OPENAI_MODEL': os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o'),
    }


# Load initial values
_config_values = _load_config()


class Config:
    """Configuration class for MCP MongoDB search application"""
    
    # MongoDB Configuration
    MONGODB_CONNECTION_STRING: str = _config_values['MONGODB_CONNECTION_STRING']
    MONGODB_DATABASE: str = _config_values['MONGODB_DATABASE']
    
    # MCP Server Configuration
    MCP_SERVER_COMMAND: Optional[list] = None  # Will use default if None
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Query Configuration
    DEFAULT_QUERY_LIMIT: int = int(os.getenv('DEFAULT_QUERY_LIMIT', '10'))
    
    # Application Configuration
    APP_NAME: str = "MCP MongoDB Search Solution"
    APP_VERSION: str = "1.0.0"
    
    # Azure OpenAI Configuration
    AZURE_OPENAI_ENDPOINT: str = _config_values['AZURE_OPENAI_ENDPOINT']
    AZURE_OPENAI_API_KEY: str = _config_values['AZURE_OPENAI_API_KEY']
    AZURE_OPENAI_API_VERSION: str = _config_values['AZURE_OPENAI_API_VERSION']
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: str = _config_values['AZURE_OPENAI_CHAT_DEPLOYMENT_NAME']
    AZURE_OPENAI_MODEL: str = _config_values['AZURE_OPENAI_MODEL']
    
    @classmethod
    def get_mongodb_uri(cls) -> str:
        """Get MongoDB connection URI"""
        return cls.MONGODB_CONNECTION_STRING
    
    @classmethod
    def get_database_name(cls) -> str:
        """Get database name"""
        return cls.MONGODB_DATABASE
    
    @classmethod
    def reload(cls):
        """Reload configuration from environment"""
        global _config_values
        _config_values = _load_config()
        cls.MONGODB_CONNECTION_STRING = _config_values['MONGODB_CONNECTION_STRING']
        cls.MONGODB_DATABASE = _config_values['MONGODB_DATABASE']
        cls.AZURE_OPENAI_ENDPOINT = _config_values['AZURE_OPENAI_ENDPOINT']
        cls.AZURE_OPENAI_API_KEY = _config_values['AZURE_OPENAI_API_KEY']
        cls.AZURE_OPENAI_API_VERSION = _config_values['AZURE_OPENAI_API_VERSION']
        cls.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME = _config_values['AZURE_OPENAI_CHAT_DEPLOYMENT_NAME']
        cls.AZURE_OPENAI_MODEL = _config_values['AZURE_OPENAI_MODEL']
    
    @classmethod
    def validate(cls) -> bool:
        """
        Validate configuration
        
        Returns:
            True if configuration is valid
        """
        if not cls.MONGODB_CONNECTION_STRING:
            raise ValueError("MONGODB_CONNECTION_STRING is required")
        
        if not cls.MONGODB_DATABASE:
            raise ValueError("MONGODB_DATABASE is required")
        
        return True
