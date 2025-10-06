"""
Application configuration using Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # App settings
    PROJECT_NAME: str = "InvestWise-Predictor"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/v1"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1", "*"]
    
    # Database settings
    DATABASE_URL: str = "postgresql://investwise:investwise@localhost:5432/investwise"
    
    # Redis settings
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # Authentication settings
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    
    # ML Service settings
    ML_SERVICE_URL: str = "http://localhost:8000"
    MLFLOW_TRACKING_URI: str = "http://localhost:5000"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # Monitoring
    ENABLE_METRICS: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()