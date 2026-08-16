"""
Central configuration — reads every tuneable from environment variables
so no secret ever lands in source code.

Uses pydantic-settings: just set the values in `backend/.env` locally,
or in the hosting platform's env-var dashboard for prod.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # ── Database ────────────────────────────────────────────────────────
    # SQLite locally, PostgreSQL in prod — swap with a single env var.
    DATABASE_URL: str = "sqlite:///./app.db"

    # ── LLM ─────────────────────────────────────────────────────────────
    ANTHROPIC_API_KEY: str = ""

    # ── Auth ────────────────────────────────────────────────────────────
    JWT_SECRET: str = "change-me-in-production"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 60 * 24  # 24 hours

    # ── Frontend ────────────────────────────────────────────────────────
    FRONTEND_ORIGIN: str = "http://localhost:3000"


settings = Settings()
