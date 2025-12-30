"""Application configuration settings."""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "User REST API"
    app_version: str = "2.0.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./users.db"
    # For PostgreSQL: "postgresql://user:password@localhost/dbname"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

