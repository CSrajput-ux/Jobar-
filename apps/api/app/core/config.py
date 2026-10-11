from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    PROJECT_NAME: str = "JobPilot Core API"
    VERSION: str = "0.1.0"
    API_V1_STR: str = "/api/v1"
    ENVIRONMENT: str = "development"

    DATABASE_URL: str = ""
    REDIS_URL: str = ""
    S3_ENDPOINT: str = ""
    S3_ACCESS_KEY: str = ""
    S3_SECRET_KEY: str = ""
    S3_BUCKET_NAME: str = "jobpilot-assets"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-5-sonnet-20241022"
    ENCRYPTION_MASTER_KEY: str = ""
    HUNTER_API_KEY: str = ""
    APOLLO_API_KEY: str = ""

    MAX_APPLICATIONS_PER_HOUR: int = 5
    GLOBAL_DAILY_APPLY_CAP: int = 20
    CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @model_validator(mode="after")
    def validate_required_settings(self):
        if self.ENVIRONMENT == "production":
            required = {
                "DATABASE_URL": self.DATABASE_URL,
                "REDIS_URL": self.REDIS_URL,
                "ENCRYPTION_MASTER_KEY": self.ENCRYPTION_MASTER_KEY,
            }
            missing = [name for name, value in required.items() if not value]
            if missing:
                raise ValueError(f"Missing production settings: {', '.join(missing)}")
            
            # Validate encryption key length in production (must be 32 bytes = 64 hex chars)
            try:
                key_bytes = bytes.fromhex(self.ENCRYPTION_MASTER_KEY)
                if len(key_bytes) != 32:
                    raise ValueError(f"ENCRYPTION_MASTER_KEY must be exactly 32 bytes (64 hex characters), got {len(key_bytes)} bytes")
            except ValueError as e:
                raise ValueError(f"Invalid production ENCRYPTION_MASTER_KEY: {e}")

        return self

    def get_database_url(self) -> str:
        """Returns normalized async database URL."""
        if not self.DATABASE_URL:
            # Safe local fallback for testing/dev
            return "sqlite+aiosqlite:///jobpilot.db"
        url = self.DATABASE_URL
        if url.startswith("postgresql://"):
            return url.replace("postgresql://", "postgresql+asyncpg://", 1)
        if url.startswith("sqlite://") and not url.startswith("sqlite+aiosqlite://"):
            return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
        return url


settings = Settings()

