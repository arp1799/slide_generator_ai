from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    # API Configuration
    api_title: str = "Slide Generator API"
    api_description: str = "A powerful API for generating customizable presentation slides"
    api_version: str = "1.0.0"
    
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    
    # Hugging Face Configuration
    huggingface_model: str = "microsoft/DialoGPT-medium"
    huggingface_token: Optional[str] = None
    
    # Redis Configuration (for caching)
    redis_url: str = "redis://localhost:6379"
    
    # Rate Limiting
    rate_limit_per_minute: int = 60
    
    # File Storage
    output_dir: str = "samples"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    
    # Slide Configuration
    max_slides: int = 20
    min_slides: int = 1
    
    # Production Settings
    environment: str = "development"
    debug: bool = False
    log_level: str = "INFO"
    
    # CORS Settings
    cors_origins: list = ["*"]
    cors_allow_credentials: bool = True
    cors_allow_methods: list = ["*"]
    cors_allow_headers: list = ["*"]
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False
    }


settings = Settings()

# Ensure output directory exists
os.makedirs(settings.output_dir, exist_ok=True) 