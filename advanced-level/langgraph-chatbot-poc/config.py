"""
Configuration management for LangGraph Chatbot POC
"""

import os
import logging
from dotenv import load_dotenv
from typing import Optional

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class Config:
    """Configuration class for LangGraph Chatbot"""
    
    # OpenAI Configuration
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL: str = os.getenv('OPENAI_MODEL', 'gpt-4o')
    
    # Azure OpenAI Configuration (alternative)
    AZURE_OPENAI_ENDPOINT: Optional[str] = os.getenv('AZURE_OPENAI_ENDPOINT')
    AZURE_OPENAI_API_KEY: Optional[str] = os.getenv('AZURE_OPENAI_API_KEY')
    AZURE_OPENAI_API_VERSION: str = os.getenv('AZURE_OPENAI_API_VERSION', '2024-06-01')
    AZURE_OPENAI_CHAT_DEPLOYMENT_NAME: Optional[str] = os.getenv('AZURE_OPENAI_CHAT_DEPLOYMENT_NAME')
    AZURE_OPENAI_MODEL: str = os.getenv('AZURE_OPENAI_MODEL', 'gpt-4o')
    
    # Weather API Configuration
    OPENWEATHERMAP_API_KEY: Optional[str] = os.getenv('OPENWEATHERMAP_API_KEY')
    
    # Flask Configuration
    FLASK_PORT: int = int(os.getenv('FLASK_PORT', 5002))
    FLASK_DEBUG: bool = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration"""
        # Check Azure OpenAI (preferred)
        has_azure = (
            cls.AZURE_OPENAI_ENDPOINT and 
            cls.AZURE_OPENAI_API_KEY and 
            cls.AZURE_OPENAI_CHAT_DEPLOYMENT_NAME
        )
        
        # Check OpenAI (fallback)
        has_openai = cls.OPENAI_API_KEY
        
        if not has_azure and not has_openai:
            raise ValueError(
                "LLM configuration required. Set either:\n"
                "  - Azure OpenAI: AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY, AZURE_OPENAI_CHAT_DEPLOYMENT_NAME\n"
                "  - OR OpenAI: OPENAI_API_KEY"
            )
        
        if has_azure:
            logger.info("✓ Azure OpenAI configured (preferred)")
        elif has_openai:
            logger.info("✓ OpenAI configured (fallback)")
        
        return True

