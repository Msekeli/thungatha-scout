import argparse
import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from psycopg.connection import Connection

from scout.persistence.database_connection import get_database_connection
from scout.registry_employer_importer import import_employer
from scout.registry_loader import REGISTRY_DIRECTORY
from scout.registry_source_importer import (
    SUPPORTED_IMPORT_ADAPTERS,
    import_employer_sources,
)


def import_registry(
    registry: dict[str, Any],
    connection: Connection,
    adapter_key: str | None = None,
) -> dict[str, int]:
    counts = {
        "employers_created": 0,
        "employers_updated": 0,
        "sources_created": 0,
        "sources_updated": 0,
        "sources_skipped": 0,
    }
    for item in registry["employers"]:
        registry_sources = item.get("sources", [])
        if adapter_key:
            registry_sources = [
                source
                for source in registry_sources
                if source.get("ats") == adapter_key
            ]
        supported = [
            source
            for source in registry_sources
            if source.get("ats") in SUPPORTED_IMPORT_ADAPTERS
        ]
        counts["sources_skipped"] += len(registry_sources) - len(supported)
        if not supported:
            continue
        employer = import_employer(item, connection, counts)
        import_employer_sources(
            {**item, "sources": supported},
            employer,
            item.get("careers_url"),
            connection,
            counts,
        )
    return counts


def import_employer_registry(
    connection_factory: Callable[[], Connection] = get_database_connection,
    registry_path: Path | None = None,
    adapter_key: str | None = None,
) -> dict[str, int]:
    path = registry_path or (REGISTRY_DIRECTORY / "employer-source-registry.json")
    registry = json.loads(path.read_text(encoding="utf-8"))
    with connection_factory() as connection, connection.transaction():
        return import_registry(registry, connection, adapter_key)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import registered employer sources.")
    parser.add_argument(
        "--adapter",
        choices=sorted(SUPPORTED_IMPORT_ADAPTERS),
        help="Import only sources for this ATS adapter.",
    )
    args = parser.parse_args()
    result = import_employer_registry(adapter_key=args.adapter)
    print(
        "Registry import complete: "
        f"{result['employers_created']} employers created, "
        f"{result['employers_updated']} existing employers updated, "
        f"{result['sources_created']} sources created, "
        f"{result['sources_updated']} sources updated, "
        f"{result['sources_skipped']} unsupported sources skipped."
    )


if __name__ == "__main__":
    main()
