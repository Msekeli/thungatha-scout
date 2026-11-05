from typing import Any

import psycopg
from psycopg.connection import Connection
from psycopg.rows import dict_row
from pydantic import SecretStr

from scout.settings import Settings, get_settings


class DatabaseConfigurationError(RuntimeError):
    """Raised when the Scout database connection is not configured."""


def get_database_connection(
    settings: Settings | None = None,
) -> Connection[dict[str, Any]]:
    configured_settings = settings or get_settings()
    database_url: SecretStr | None = configured_settings.scout_database_url

    if database_url is None:
        raise DatabaseConfigurationError(
            "SCOUT_DATABASE_URL must be configured before database access."
        )

    return psycopg.connect(
        database_url.get_secret_value(),
        connect_timeout=10,
        prepare_threshold=None,
        row_factory=dict_row,
        sslmode="require",
    )
