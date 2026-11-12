import pytest
from pydantic import SecretStr, ValidationError

from scout.settings import Settings


def test_database_url_is_loaded_as_a_secret(monkeypatch) -> None:
    database_url = "postgresql://user:password@host:6543/postgres"
    monkeypatch.setenv("SCOUT_DATABASE_URL", database_url)
    settings = Settings(_env_file=None)
    assert isinstance(settings.scout_database_url, SecretStr)
    assert settings.scout_database_url.get_secret_value() == database_url
    assert "password" not in str(settings.scout_database_url)


def test_database_url_is_optional_when_not_configured(monkeypatch) -> None:
    monkeypatch.delenv("SCOUT_DATABASE_URL", raising=False)
    assert Settings(_env_file=None).scout_database_url is None


def test_supabase_auth_settings_keep_publishable_key_secret(monkeypatch) -> None:
    monkeypatch.setenv("SCOUT_SUPABASE_URL", "https://scout.supabase.co")
    monkeypatch.setenv("SCOUT_SUPABASE_PUBLISHABLE_KEY", "public-key")
    monkeypatch.setenv("SCOUT_ADMIN_EMAIL", "admin@example.com")
    settings = Settings(_env_file=None)
    assert settings.scout_supabase_url == "https://scout.supabase.co"
    assert isinstance(settings.scout_supabase_publishable_key, SecretStr)
    assert settings.scout_supabase_publishable_key.get_secret_value() == "public-key"
    assert settings.scout_admin_email == "admin@example.com"
    assert "public-key" not in str(settings.scout_supabase_publishable_key)


def test_ai_and_crawler_are_disabled_by_default() -> None:
    settings = Settings(_env_file=None)
    assert settings.ai_enabled is False
    assert settings.crawler_enabled is False
    assert settings.ai_primary_provider == "gemini"
    assert settings.crawler_respect_robots_txt is True


def test_ai_provider_keys_are_secret_values(monkeypatch) -> None:
    monkeypatch.setenv("GEMINI_API_KEY", "gemini-secret")
    monkeypatch.setenv("GROQ_API_KEY", "groq-secret")
    settings = Settings(_env_file=None)
    assert isinstance(settings.gemini_api_key, SecretStr)
    assert isinstance(settings.groq_api_key, SecretStr)
    assert "gemini-secret" not in str(settings.gemini_api_key)
    assert "groq-secret" not in str(settings.groq_api_key)


def test_ai_provider_and_crawler_limits_are_configurable(monkeypatch) -> None:
    monkeypatch.setenv("AI_PRIMARY_PROVIDER", "groq")
    monkeypatch.setenv("CRAWLER_MAX_CONCURRENCY", "5")
    settings = Settings(_env_file=None)
    assert settings.ai_primary_provider == "groq"
    assert settings.crawler_max_concurrency == 5


def test_invalid_provider_and_out_of_range_limits_are_rejected(monkeypatch) -> None:
    monkeypatch.setenv("AI_PRIMARY_PROVIDER", "unknown")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
    monkeypatch.delenv("AI_PRIMARY_PROVIDER")
    monkeypatch.setenv("CRAWLER_MAX_CONCURRENCY", "99")
    with pytest.raises(ValidationError):
        Settings(_env_file=None)
