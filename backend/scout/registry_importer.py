import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from psycopg.connection import Connection
from psycopg.types.json import Jsonb

from scout.persistence.database_connection import get_database_connection
from scout.registry_loader import REGISTRY_DIRECTORY, validate_source_config


def import_registry(
    registry: dict[str, Any],
    connection: Connection,
) -> dict[str, int]:
    counts = {
        "employers_created": 0,
        "sources_created": 0,
        "sources_updated": 0,
    }

    for item in registry["employers"]:
        employer = connection.execute(
            """
            SELECT id, website_url FROM employers
            WHERE name = %s ORDER BY created_at, id LIMIT 1
            """,
            (item["name"],),
        ).fetchone()
        careers_url = item.get("careers_url")
        if employer is not None and employer["website_url"] not in (
            None, careers_url
        ):
            raise ValueError(
                f"Employer name already exists with another website: {item['name']}"
            )
        if employer is None:
            location_evidence = []
            if item.get("cape_town_presence_claimed"):
                location_evidence.append({
                    "claim": "Cape Town presence",
                    "status": item.get(
                        "cape_town_presence_status",
                        "pending_verification",
                    ),
                })
            employer = connection.execute(
                """
                INSERT INTO employers (
                    name, website_url, organization_type, status,
                    location_evidence
                )
                VALUES (%s, %s, %s, 'discovered', %s)
                RETURNING id, website_url
                """,
                (
                    item["name"],
                    careers_url,
                    item.get("organization_classification", "unresolved"),
                    Jsonb(location_evidence),
                ),
            ).fetchone()
            counts["employers_created"] += 1

        for source in item.get("sources", []):
            adapter_key = source.get("ats")
            if adapter_key not in {"greenhouse", "workday"}:
                raise ValueError(
                    f"Unsupported V1 adapter '{adapter_key}' in the "
                    "Greenhouse/Workday registry."
                )

            adapter_config = source.get("config", {})
            validate_source_config(adapter_key, adapter_config)
            source_url = source["official_source_url"]
            existing = connection.execute(
                """
                SELECT id, employer_id, adapter_key
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
                continue

            employer_sources = connection.execute(
                """
                SELECT id, normalized_url
                FROM employer_sources
                WHERE employer_id = %s AND adapter_key = %s
                ORDER BY created_at, id
                """,
                (employer["id"], adapter_key),
            ).fetchall()
            if len(employer_sources) > 1:
                raise ValueError(
                    f"Cannot safely reconcile multiple {adapter_key} sources "
                    f"for employer: {item['name']}"
                )
            if employer_sources:
                connection.execute(
                    """
                    UPDATE employer_sources
                    SET source_url = %s,
                        normalized_url = %s,
                        adapter_config = %s,
                        updated_at = NOW()
                    WHERE id = %s
                    """,
                    (
                        source_url,
                        source_url,
                        Jsonb(adapter_config),
                        employer_sources[0]["id"],
                    ),
                )
                counts["sources_updated"] += 1
                continue

            evidence = [
                {"url": url, "status": "claimed"}
                for url in source.get("verification_evidence", [])
            ]
            connection.execute(
                """
                INSERT INTO employer_sources (
                    employer_id, adapter_key, source_url,
                    employer_careers_url, normalized_url, adapter_config,
                    status, permission_status, relationship_evidence
                )
                VALUES (%s, %s, %s, %s, %s, %s,
                        'discovered', 'unknown', %s)
                """,
                (
                    employer["id"],
                    adapter_key,
                    source_url,
                    careers_url,
                    source_url,
                    Jsonb(adapter_config),
                    Jsonb(evidence),
                ),
            )
            counts["sources_created"] += 1

    return counts


def import_employer_registry(
    connection_factory: Callable[[], Connection] = get_database_connection,
    registry_path: Path | None = None,
) -> dict[str, int]:
    path = registry_path or (
        REGISTRY_DIRECTORY / "v1-supported-ats-employer-sources.json"
    )
    registry = json.loads(path.read_text(encoding="utf-8"))
    with connection_factory() as connection, connection.transaction():
        return import_registry(registry, connection)


if __name__ == "__main__":
    result = import_employer_registry()
    print(
        "Registry import complete: "
        f"{result['employers_created']} employers created, "
        f"{result['sources_created']} sources created."
    )
