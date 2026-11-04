from pathlib import Path

from psycopg.connection import Connection

from scout.persistence.database_connection import get_database_connection
from scout.persistence.migration_catalog import (
    MigrationChecksumError,
    discover_migrations,
    migration_checksum,
)

MIGRATION_LOCK_ID = 731_204_119


def apply_migrations(
    connection: Connection,
    directory: Path | None = None,
) -> list[str]:
    migration_directory = directory or (
        Path(__file__).resolve().parents[2] / "database-migrations"
    )
    migrations = discover_migrations(migration_directory)
    applied_versions: list[str] = []

    with connection.transaction():
        connection.execute(
            "SELECT pg_advisory_xact_lock(%s)",
            (MIGRATION_LOCK_ID,),
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS scout_schema_migrations (
                version TEXT PRIMARY KEY,
                checksum TEXT NOT NULL,
                applied_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
            )
            """
        )
        existing = {
            row["version"]: row["checksum"]
            for row in connection.execute(
                "SELECT version, checksum FROM scout_schema_migrations"
            ).fetchall()
        }
        for migration in migrations:
            version = migration.name[:4]
            checksum = migration_checksum(migration)
            if version in existing:
                if existing[version] != checksum:
                    raise MigrationChecksumError(
                        f"Applied migration {version} has changed."
                    )
                continue
            connection.execute(migration.read_text(encoding="utf-8"), prepare=False)
            connection.execute(
                """
                INSERT INTO scout_schema_migrations (version, checksum)
                VALUES (%s, %s)
                """,
                (version, checksum),
            )
            applied_versions.append(version)
    return applied_versions


def run_migrations() -> list[str]:
    with get_database_connection() as connection:
        return apply_migrations(connection)


if __name__ == "__main__":
    applied = run_migrations()
    print(f"Applied migrations: {', '.join(applied) if applied else 'none'}")
