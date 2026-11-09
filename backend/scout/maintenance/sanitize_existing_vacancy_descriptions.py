import argparse
import hashlib
from typing import Any

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.persistence.database_connection import get_database_connection

BACKUP_TABLE = "vacancy_description_sanitization_backups"


def prepare_changes(rows: list[dict[str, Any]]) -> list[tuple[Any, str, str]]:
    changes = []
    for row in rows:
        original = row["description"]
        if original is None:
            continue
        sanitized = sanitize_vacancy_description(original)
        if sanitized != original:
            changes.append((row["id"], original, sanitized))
    return changes


def apply_changes(connection: Any, changes: list[tuple[Any, str, str]]) -> int:
    connection.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {BACKUP_TABLE} (
            vacancy_id UUID NOT NULL,
            original_sha256 CHAR(64) NOT NULL,
            original_description TEXT NOT NULL,
            backed_up_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
            PRIMARY KEY (vacancy_id, original_sha256)
        )
        """
    )
    updated = 0
    for vacancy_id, original, sanitized in changes:
        result = connection.execute(
            """
            UPDATE vacancies
            SET description = %s, updated_at = NOW()
            WHERE id = %s AND description = %s
            """,
            (sanitized, vacancy_id, original),
        )
        if result.rowcount != 1:
            continue
        digest = hashlib.sha256(original.encode("utf-8")).hexdigest()
        connection.execute(
            f"""
            INSERT INTO {BACKUP_TABLE} (
                vacancy_id, original_sha256, original_description
            )
            VALUES (%s, %s, %s)
            ON CONFLICT (vacancy_id, original_sha256) DO NOTHING
            """,
            (vacancy_id, digest, original),
        )
        updated += 1
    return updated


def main() -> None:
    parser = argparse.ArgumentParser(description="Backfill sanitized vacancy HTML.")
    parser.add_argument("--apply", action="store_true", help="Back up and update rows.")
    args = parser.parse_args()
    with get_database_connection() as connection:
        rows = connection.execute(
            "SELECT id, description FROM vacancies WHERE description IS NOT NULL"
        ).fetchall()
        changes = prepare_changes(rows)
        print(f"Vacancies checked: {len(rows)}")
        print(f"Descriptions needing changes: {len(changes)}")
        if not args.apply:
            print("Dry run only. Re-run with --apply to back up and update.")
            return
        with connection.transaction():
            updated = apply_changes(connection, changes)
        print(f"Descriptions updated: {updated}")
        print(f"Original descriptions backed up in {BACKUP_TABLE}.")


if __name__ == "__main__":
    main()
