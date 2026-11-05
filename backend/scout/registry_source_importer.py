from typing import Any

from psycopg.connection import Connection
from psycopg.types.json import Jsonb

from scout.registry_loader import validate_source_config


def _update_source(
    connection: Connection,
    source_id: Any,
    source_url: str,
    adapter_config: dict[str, Any],
    include_normalized_url: bool = False,
) -> None:
    if include_normalized_url:
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


def _create_source(
    item: dict[str, Any],
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


def import_employer_sources(
    item: dict[str, Any],
    employer: dict[str, Any],
    careers_url: str | None,
    connection: Connection,
    counts: dict[str, int],
) -> None:
    for source in item.get("sources", []):
        adapter_key = source.get("ats")
        if adapter_key not in {"greenhouse", "workday"}:
            raise ValueError(
                f"Unsupported V1 adapter '{adapter_key}' in the "
                "Greenhouse/Workday registry."
            )
        config = source.get("config", {})
        validate_source_config(adapter_key, config)
        source_url = source["official_source_url"]
        existing = connection.execute(
            """
            SELECT id, employer_id, adapter_key, source_url, adapter_config
            FROM employer_sources WHERE normalized_url = %s
            """,
            (source_url,),
        ).fetchone()
        if existing is not None:
            if (
                existing["employer_id"] != employer["id"]
                or existing["adapter_key"] != adapter_key
            ):
                raise ValueError(
                    f"Source URL is already assigned elsewhere: {source_url}"
                )
            if (
                existing["source_url"] != source_url
                or existing["adapter_config"] != config
            ):
                _update_source(connection, existing["id"], source_url, config)
                counts["sources_updated"] += 1
            continue

        matches = connection.execute(
            """
            SELECT id, normalized_url FROM employer_sources
            WHERE employer_id = %s AND adapter_key = %s
            ORDER BY created_at, id
            """,
            (employer["id"], adapter_key),
        ).fetchall()
        if len(matches) > 1:
            raise ValueError(
                f"Cannot safely reconcile multiple {adapter_key} sources "
                f"for employer: {item['name']}"
            )
        if matches:
            _update_source(connection, matches[0]["id"], source_url, config, True)
            counts["sources_updated"] += 1
            continue
        _create_source(item, source, employer, careers_url, connection)
        counts["sources_created"] += 1
