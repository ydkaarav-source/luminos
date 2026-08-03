"""
Central application configuration.

All configuration is env-driven (12-factor style). Nothing here should
ever contain a literal secret - only defaults safe for local dev.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- App ---
    APP_NAME: str = "LuminOS"
    ENVIRONMENT: str = "development"  # development | staging | production
    API_V1_PREFIX: str = "/api/v1"

    # --- Security ---
    SECRET_KEY: str = "change-me-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Database ---
    DATABASE_URL: str = (
        "postgresql+psycopg2://luminos:luminos@localhost:5432/luminos"
    )

    # --- AI Provider ---
    AI_PROVIDER: str = "openai"  # swap this to add new providers
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache
def get_settings() -> Settings:
    """Cached settings instance - env is read once per process."""
    return Settings()


settings = get_settings()
