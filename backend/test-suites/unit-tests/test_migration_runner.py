from pathlib import Path

import pytest

from scout.persistence.migration_runner import (
    discover_migrations,
    migration_checksum,
)


def test_migrations_are_discovered_in_version_order(tmp_path: Path) -> None:
    later = tmp_path / "0002-add-source-index.sql"
    earlier = tmp_path / "0001-create-employers.sql"
    later.write_text("SELECT 2;", encoding="utf-8")
    earlier.write_text("SELECT 1;", encoding="utf-8")

    assert discover_migrations(tmp_path) == [earlier, later]


def test_migration_filename_must_have_a_version_and_description(
    tmp_path: Path,
) -> None:
    (tmp_path / "initial.sql").write_text("SELECT 1;", encoding="utf-8")

    with pytest.raises(ValueError, match="Invalid migration filename"):
        discover_migrations(tmp_path)


def test_migration_checksum_changes_when_file_changes(tmp_path: Path) -> None:
    migration = tmp_path / "0001-create-employers.sql"
    migration.write_text("SELECT 1;", encoding="utf-8")
    first_checksum = migration_checksum(migration)

    migration.write_text("SELECT 2;", encoding="utf-8")

    assert migration_checksum(migration) != first_checksum


def test_missing_migration_directory_fails_clearly(tmp_path: Path) -> None:
    missing_directory = tmp_path / "missing-migrations"

    with pytest.raises(FileNotFoundError, match="Migration directory does not exist"):
        discover_migrations(missing_directory)
