from typing import Any

from psycopg.types.json import Jsonb

from scout.persistence.database_connection import get_database_connection
from scout.registry_loader import REGISTRY_DIRECTORY


def import_employer_registry() -> dict[str, int]:
    import json

    registry_path = REGISTRY_DIRECTORY / "employer-source-registry.json"
    registry: dict[str, Any] = json.loads(
        registry_path.read_text(encoding="utf-8")
    )
    counts = {"employers_created": 0, "sources_created": 0, "sources_skipped": 0}

    with get_database_connection() as connection, connection.transaction():
        for item in registry["employers"]:
            employer = connection.execute(
                """
                SELECT id FROM employers
                WHERE name = %s AND website_url IS NOT DISTINCT FROM %s
                ORDER BY created_at, id LIMIT 1
                """,
                (item["name"], item.get("careers_url")),
            ).fetchone()
            if employer is None:
                pending_location = []
                if item.get("cape_town_presence_claimed"):
                    pending_location = [{
                        "claim": "Cape Town presence",
                        "status": item.get(
                            "cape_town_presence_status",
                            "pending_verification",
                        ),
                    }]
                employer = connection.execute(
                    """
                    INSERT INTO employers (
                        name, website_url, organization_type, status,
                        location_evidence
                    )
                    VALUES (%s, %s, %s, 'discovered', %s)
                    RETURNING id
                    """,
                    (
                        item["name"],
                        item.get("careers_url"),
                        item.get("organization_classification", "unresolved"),
                        Jsonb(pending_location),
                    ),
                ).fetchone()
                counts["employers_created"] += 1

            for source in item.get("sources", []):
                adapter_key = source.get("ats")
                if adapter_key not in {"greenhouse", "workday"}:
                    counts["sources_skipped"] += 1
                    continue

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
                        item.get("careers_url"),
                        source_url,
                        Jsonb(source.get("config", {})),
                        Jsonb(evidence),
                    ),
                )
                counts["sources_created"] += 1

    return counts


if __name__ == "__main__":
    result = import_employer_registry()
    print(
        "Registry import complete: "
        f"{result['employers_created']} employers created, "
        f"{result['sources_created']} sources created, "
        f"{result['sources_skipped']} unsupported sources skipped."
    )
