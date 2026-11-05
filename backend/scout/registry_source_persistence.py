from typing import Any

from psycopg.connection import Connection
from psycopg.types.json import Jsonb


def update_source(
    connection: Connection,
    source_id: Any,
    source_url: str,
    adapter_config: dict[str, Any],
    update_normalized_url: bool = False,
) -> None:
    if update_normalized_url:
        connection.execute(
            """
            UPDATE employer_sources
            SET source_url = %s, normalized_url = %s,
                adapter_config = %s, updated_at = NOW()
            WHERE id = %s
            """,
            (source_url, source_url, Jsonb(adapter_config), source_id),
        )
        return
    connection.execute(
        """
        UPDATE employer_sources
        SET source_url = %s, adapter_config = %s, updated_at = NOW()
        WHERE id = %s
        """,
        (source_url, Jsonb(adapter_config), source_id),
    )


def create_source(
    source: dict[str, Any],
    employer: dict[str, Any],
    careers_url: str | None,
    connection: Connection,
) -> None:
    evidence = [
        {"url": url, "status": "claimed"}
        for url in source.get("verification_evidence", [])
    ]
    connection.execute(
        """
        INSERT INTO employer_sources (
            employer_id, adapter_key, source_url, employer_careers_url,
            normalized_url, adapter_config, status, permission_status,
            relationship_evidence
        )
        VALUES (%s, %s, %s, %s, %s, %s, 'discovered', 'unknown', %s)
        """,
        (
            employer["id"],
            source["ats"],
            source["official_source_url"],
            careers_url,
            source["official_source_url"],
            Jsonb(source.get("config", {})),
            Jsonb(evidence),
        ),
    )
