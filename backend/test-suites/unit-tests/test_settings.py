from pydantic import SecretStr

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

    settings = Settings(_env_file=None)

    assert settings.scout_database_url is None


def test_supabase_auth_settings_keep_publishable_key_secret(
    monkeypatch,
) -> None:
    monkeypatch.setenv("SCOUT_SUPABASE_URL", "https://scout.supabase.co")
    monkeypatch.setenv("SCOUT_SUPABASE_PUBLISHABLE_KEY", "public-key")
    monkeypatch.setenv("SCOUT_ADMIN_EMAIL", "admin@example.com")

    settings = Settings(_env_file=None)

    assert settings.scout_supabase_url == "https://scout.supabase.co"
    assert isinstance(settings.scout_supabase_publishable_key, SecretStr)
    assert settings.scout_supabase_publishable_key.get_secret_value() == (
        "public-key"
    )
    assert settings.scout_admin_email == "admin@example.com"
    assert "public-key" not in str(settings.scout_supabase_publishable_key)
