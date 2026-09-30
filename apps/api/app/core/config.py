import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "JobPilot Core API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    
    # Environment
    ENVIRONMENT: str = os.getenv("NODE_ENV", "development")
    
    # Database & Redis
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://jobpilot:jobpilot_secret@localhost:5432/jobpilot_db")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # S3 / MinIO
    S3_ENDPOINT: str = os.getenv("S3_ENDPOINT", "http://localhost:9000")
    S3_ACCESS_KEY: str = os.getenv("S3_ACCESS_KEY", "minioadmin")
    S3_SECRET_KEY: str = os.getenv("S3_SECRET_KEY", "minioadmin")
    S3_BUCKET_NAME: str = os.getenv("S3_BUCKET_NAME", "jobpilot-assets")
    
    # AI / LLM
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL: str = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet-20241022")
    
    # Security: AES-256 Master Key (hex string 32 bytes)
    ENCRYPTION_MASTER_KEY: str = os.getenv(
        "ENCRYPTION_MASTER_KEY", 
        "0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef"
    )
    
    # Hunter & Apollo
    HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")
    APOLLO_API_KEY: str = os.getenv("APOLLO_API_KEY", "")
    
    # System Rate Limits
    MAX_APPLICATIONS_PER_HOUR: int = int(os.getenv("MAX_APPLICATIONS_PER_HOUR", "5"))
    GLOBAL_DAILY_APPLY_CAP: int = int(os.getenv("GLOBAL_DAILY_APPLY_CAP", "20"))
    
    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
