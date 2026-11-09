from typing import Any

from psycopg.connection import Connection

from scout.registry_loader import validate_source_config
from scout.registry_source_persistence import create_source, update_source


SUPPORTED_IMPORT_ADAPTERS = {"greenhouse", "lever", "workday"}


def import_employer_sources(
    item: dict[str, Any],
    employer: dict[str, Any],
    careers_url: str | None,
    connection: Connection,
    counts: dict[str, int],
) -> None:
    for source in item.get("sources", []):
        adapter_key = source.get("ats")
        if adapter_key not in SUPPORTED_IMPORT_ADAPTERS:
            counts["sources_skipped"] += 1
            continue
        config = source.get("config", {})
        validate_source_config(adapter_key, config)
        source_url = source["official_source_url"]
        existing = connection.execute(
            """
            SELECT id, employer_id, adapter_key, source_url, adapter_config,
                   employer_careers_url
            FROM employer_sources WHERE normalized_url = %s
            """,
            (source_url,),
        ).fetchone()
        if existing is not None:
            assigned_elsewhere = (
                existing["employer_id"] != employer["id"]
                or existing["adapter_key"] != adapter_key
            )
            if assigned_elsewhere:
                raise ValueError(
                    f"Source URL is already assigned elsewhere: {source_url}"
                )
            changed = (
                existing["source_url"] != source_url
                or existing["adapter_config"] != config
                or existing.get("employer_careers_url") != careers_url
            )
            if changed:
                update_source(
                    connection, existing["id"], source_url, config, careers_url
                )
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
            update_source(
                connection, matches[0]["id"], source_url, config,
                careers_url, update_normalized_url=True,
            )
            counts["sources_updated"] += 1
            continue
        create_source(source, employer, careers_url, connection)
        counts["sources_created"] += 1
