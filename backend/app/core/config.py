from pydantic_settings import BaseSettings
from typing import List
from pathlib import Path

# Resolve .env from the repo root (two levels up from this file: app/core/ → app/ → backend/ → repo root)
_ENV_FILE = Path(__file__).resolve().parents[3] / ".env"


class Settings(BaseSettings):
    # App
    app_env: str = "development"
    secret_key: str = "change-me-in-production"

    # API protection
    api_secret: str = ""

    # CORS
    cors_origins: str = "https://sushanthtws.github.io"

    @property
    def cors_origins_list(self) -> List[str]:
        return [o.strip() for o in self.cors_origins.split(",")]

    # Database
    database_url: str = "postgresql://synapse:synapse_dev@localhost:5432/synapse"
    base_skill_dir: str = "/Users/sushanths/synapse_github/data/skills_repo"

    # LLM
    groq_api_key: str = ""
    openai_api_key: str = ""

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # GCS (used in production for skill file storage)
    gcs_bucket: str = ""

    # Server
    port: int = 8080

    class Config:
        env_file = str(_ENV_FILE)


settings = Settings()
