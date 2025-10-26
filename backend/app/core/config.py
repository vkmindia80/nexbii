from pydantic_settings import BaseSettings
from typing import List
import os

class Settings(BaseSettings):
    # Database
    MONGO_URL: str = os.getenv("MONGO_URL", "mongodb://localhost:27017/nexbii")
    POSTGRES_URL: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/nexbii_metadata")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-this-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # AI Integration
    EMERGENT_LLM_KEY: str = os.getenv("EMERGENT_LLM_KEY", "")
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://git-roadmap-1.preview.emergentagent.com",
        "https://git-roadmap-1.preview.emergentagent.com",
        "https://git-roadmap-1.preview.emergentagent.com"
    ]
    
    # Frontend URL (for password reset links)
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # App
    APP_NAME: str = "NexBII"
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()