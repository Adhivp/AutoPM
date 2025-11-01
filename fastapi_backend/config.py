"""
Configuration management using environment variables
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables
    
    Create a .env file in the project root with these variables
    """
    
    # Application settings
    APP_NAME: str = "AutoPM - Automotive Project Management Assistant"
    DEBUG: bool = False
    API_VERSION: str = "v1"
    
    # Database settings
    DATABASE_URL: str
    
    # JWT settings
    JWT_SECRET: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Encryption key for storing OAuth tokens (must be 32 url-safe base64-encoded bytes)
    ENCRYPTION_KEY: str
    
    # GitHub OAuth settings
    GITHUB_CLIENT_ID: str
    GITHUB_CLIENT_SECRET: str
    GITHUB_REDIRECT_URI: str
    
    # Jira OAuth settings
    JIRA_CLIENT_ID: str
    JIRA_CLIENT_SECRET: str
    JIRA_REDIRECT_URI: str
    
    # CORS settings
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    # Optional: Fake data generator settings (not used by main app)
    GITHUB_USERNAME: Optional[str] = None
    GITHUB_TOKEN: Optional[str] = None
    JIRA_URL: Optional[str] = None
    JIRA_EMAIL: Optional[str] = None
    JIRA_API_TOKEN: Optional[str] = None
    
    # Google Gemini AI settings
    GEMINI_API_KEY: Optional[str] = None
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": True,
        "extra": "ignore"  # Ignore extra fields in .env that aren't defined here
    }
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins from comma-separated string"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Create global settings instance
settings = Settings()
