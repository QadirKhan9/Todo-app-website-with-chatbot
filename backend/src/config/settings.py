from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
# This ensures the .env file is loaded regardless of the current working directory
import os
from dotenv import load_dotenv

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(os.path.abspath(__file__))
        )
    )
)

dotenv_path = os.path.join(PROJECT_ROOT, ".env")

load_dotenv(dotenv_path)

   


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    """
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/todo_db" )
    DATABASE_ECHO: bool = os.getenv("DATABASE_ECHO", "False").lower() == "true"

    # JWT settings (using the non-prefixed names to match the .env file)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))

    # Google Gemini settings
    GOOGLE_API_KEY: str = os.getenv("GOOGLE_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-pro")  # Updated to use current supported model

    # Redis settings for caching (from the other settings file)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_DB: int = int(os.getenv("REDIS_DB", 0))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    REDIS_CACHE_TTL: int = int(os.getenv("REDIS_CACHE_TTL", 3600))  # Default 1 hour

    # Application settings (from the other settings file)
    APP_NAME: str = "Todo AI Chatbot API"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    VERSION: str = "1.0.0"

    # CORS settings
    ALLOWED_ORIGINS: str = "*"  # In production, specify allowed origins

    # MCP Server settings
    MCP_SERVER_URL: str = "http://localhost:8000"

    class Config:
        env_file = "../../../.env"  # Look for .env file in the project root (relative to src/config/)
        env_file_encoding = 'utf-8'  # Explicitly specify encoding


def get_settings() -> Settings:
    """
    Returns the application settings instance.
    """
    return Settings()