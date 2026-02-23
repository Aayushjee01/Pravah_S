"""Application configuration using Pydantic Settings.

Loads environment variables from .env files and provides type-safe
configuration access throughout the application.
"""

from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application
    app_name: str = "Navi Mumbai House Price Predictor"
    app_version: str = "1.0.0"
    app_env: str = "development"
    app_debug: bool = False
    app_host: str = "0.0.0.0"
    app_port: int = 8000

    # CORS
    allowed_origins: str = "http://localhost:3000"

    # ML Model
    model_path: str = "models/house_price_model.joblib"

    # Logging
    log_level: str = "INFO"

    @property
    def cors_origins(self) -> List[str]:
        """Parse comma-separated CORS origins into a list."""
        return [origin.strip() for origin in self.allowed_origins.split(",")]

    @property
    def is_production(self) -> bool:
        """Check if the application is running in production."""
        return self.app_env == "production"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """Return cached application settings (singleton pattern)."""
    return Settings()
