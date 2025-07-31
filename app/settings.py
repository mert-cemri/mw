"""
Configuration settings for MAST Annotator Web.
"""
import os
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    
    # Storage Configuration
    MAST_STORAGE_PATH: Path = Path(os.getenv("MAST_STORAGE_PATH", "./data/jobs"))
    
    # API Configuration
    MAST_API_URL: str = os.getenv("MAST_API_URL", "http://localhost:3000")
    MAST_ALLOWED_ORIGINS: List[str] = [
        origin.strip() 
        for origin in os.getenv("MAST_ALLOWED_ORIGINS", "http://localhost:9000,http://localhost:8501").split(",")
    ]
    
    # File Upload Limits
    MAST_MAX_FILE_MB: int = int(os.getenv("MAST_MAX_FILE_MB", "25"))
    MAX_FILE_SIZE_BYTES: int = MAST_MAX_FILE_MB * 1024 * 1024
    
    # Testing/Development
    MAST_FAKE_MODE: bool = os.getenv("MAST_FAKE_MODE", "0") == "1"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    def __init__(self):
        """Initialize settings and create storage directory if needed."""
        self.MAST_STORAGE_PATH.mkdir(parents=True, exist_ok=True)
        
    def validate(self) -> None:
        """Validate required settings."""
        if not self.MAST_FAKE_MODE and not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is required when MAST_FAKE_MODE is disabled")


# Global settings instance
settings = Settings()