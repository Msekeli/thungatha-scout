from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Thungatha Scout API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    scout_database_url: SecretStr | None = None
    scout_supabase_url: str | None = None
    scout_supabase_publishable_key: SecretStr | None = None
    scout_admin_email: str | None = None
    scout_export_api_key: SecretStr | None = None

    ai_enabled: bool = False
    ai_primary_provider: Literal["gemini", "groq"] = "gemini"
    ai_fallback_enabled: bool = True
    ai_timeout_seconds: int = Field(default=30, ge=1, le=120)
    ai_max_output_tokens: int = Field(default=2048, ge=128, le=8192)
    ai_max_input_characters: int = Field(default=30000, ge=1000, le=100000)
    gemini_api_key: SecretStr | None = None
    gemini_model: str | None = None
    groq_api_key: SecretStr | None = None
    groq_model: str | None = None

    crawler_enabled: bool = False
    crawler_max_concurrency: int = Field(default=3, ge=1, le=10)
    crawler_max_requests_per_run: int = Field(default=100, ge=1, le=1000)
    crawler_max_depth: int = Field(default=2, ge=0, le=5)
    crawler_request_timeout_seconds: int = Field(default=30, ge=1, le=120)
    crawler_max_response_bytes: int = Field(default=2000000, ge=10000, le=10000000)
    crawler_respect_robots_txt: bool = True
    crawler_browser_fallback_enabled: bool = True

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
