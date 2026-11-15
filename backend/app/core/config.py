"""
Configuration module for the Legal Research Engine.
Uses Pydantic BaseSettings to load and validate environment variables.
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    Application configuration settings.
    """
    PROJECT_NAME: str = "SIH1701 Legal Research Engine"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["*"]
    
    # JWT Authentication
    SECRET_KEY: str = "change_this_to_a_secure_random_string_in_production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 7 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./legal_research.db"
    
    # LLM Keys & Configuration
    GEMINI_API_KEY: str | None = None
    GEMINI_PRIMARY_MODEL: str = "gemini-3.6-flash"
    GEMINI_FAST_MODEL: str = "gemini-3.5-flash-lite"
    
    GROQ_API_KEY: str | None = None
    GROQ_FALLBACK_MODEL: str = "openai/gpt-oss-120b"
    ENABLE_GROQ_FALLBACK: bool = False
    
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
