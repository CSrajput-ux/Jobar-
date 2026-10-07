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
        return self


settings = Settings()
