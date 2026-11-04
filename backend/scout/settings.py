from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Thungatha Scout API"
    app_env: str = "development"
    api_prefix: str = "/api/v1"
    scout_database_url: SecretStr | None = None
    scout_supabase_url: str | None = None
    scout_supabase_publishable_key: SecretStr | None = None
    scout_admin_email: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()
