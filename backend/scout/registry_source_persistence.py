from typing import Any
from uuid import UUID

from psycopg.connection import Connection
from psycopg.types.json import Jsonb


def update_source(
    connection: Connection,
    source_id: UUID,
    source_url: str,
    adapter_config: dict[str, Any],
    careers_url: str | None = None,
    update_normalized_url: bool = False,
) -> None:
    normalized_url = source_url if update_normalized_url else None
    connection.execute(
        """
        UPDATE employer_sources
        SET source_url = %s, employer_careers_url = %s,
            normalized_url = COALESCE(%s, normalized_url),
            adapter_config = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (source_url, careers_url, normalized_url, Jsonb(adapter_config), source_id),
    )


def create_source(
    source: dict[str, Any],
    employer: dict[str, Any],
    careers_url: str | None,
    connection: Connection,
) -> None:
    connection.execute(
        """
        INSERT INTO employer_sources (
            employer_id, adapter_key, source_url, employer_careers_url,
            normalized_url, adapter_config
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            employer["id"],
            source["ats"],
            source["official_source_url"],
            careers_url,
            source["official_source_url"],
            Jsonb(source.get("config", {})),
        ),
    )
