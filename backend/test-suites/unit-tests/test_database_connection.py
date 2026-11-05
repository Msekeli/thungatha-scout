import psycopg
import pytest
from pydantic import SecretStr

from scout.persistence.database_connection import (
    DatabaseConfigurationError,
    get_database_connection,
)
from scout.settings import Settings


def test_database_connection_uses_transaction_pooler_safe_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    captured: dict[str, object] = {}

    def fake_connect(database_url: str, **kwargs: object) -> str:
        captured["database_url"] = database_url
        captured.update(kwargs)
        return "connection"

    monkeypatch.setattr(psycopg, "connect", fake_connect)
    settings = Settings(
        _env_file=None,
        scout_database_url=SecretStr(
            "postgresql://user:password@pooler.example:6543/postgres"
        ),
    )

    result = get_database_connection(settings)

    assert result == "connection"
    assert captured["connect_timeout"] == 10
    assert captured["prepare_threshold"] is None
    assert captured["sslmode"] == "require"
    assert "password" not in str(settings.scout_database_url)


def test_database_connection_requires_a_configured_url() -> None:
    settings = Settings(_env_file=None)

    with pytest.raises(DatabaseConfigurationError):
        get_database_connection(settings)
