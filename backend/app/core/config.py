"""
Main Backend - Global Configuration Settings
============================================

File Purpose:
-------------
Loads and validates application settings, database credentials, AI service URLs,
and security parameters using Pydantic Settings.

What it does:
-------------
1. Reads environment variables from `.env` or container runtime environment.
2. Exposes strongly typed configurations (DB connection strings, service endpoint URLs, CORS origins).
3. Automatically falls back to local async SQLite (`sqlite+aiosqlite:///./medikiosk.db`)
   if PostgreSQL environment variable is not explicitly provided.
"""

import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    ENVIRONMENT: str = Field(default="development", description="Runtime environment: development/production")
    DEBUG: bool = Field(default=True, description="Enable debug logging")
    PORT: int = Field(default=8000, description="Port for backend server")

    # Database Connection String - defaults to local async SQLite if postgres not set
    DATABASE_URL: str = Field(
        default=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./medikiosk.db"),
        description="Async SQLAlchemy database URL"
    )

    # AI Service Endpoints
    DIALOGUE_SERVICE_URL: str = Field(default="http://localhost:8001", description="Dialogue AI service URL")
    OCR_SERVICE_URL: str = Field(default="http://localhost:8002", description="OCR AI service URL")
    SUMMARIZER_SERVICE_URL: str = Field(default="http://localhost:8003", description="Summarizer AI service URL")

    # Security Settings
    SECRET_KEY: str = Field(default="medikiosk-production-super-secret-key-32-chars-long", description="JWT secret key")
    ALGORITHM: str = Field(default="HS256", description="JWT cryptographic algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Session token expiry in minutes")


settings = Settings()
