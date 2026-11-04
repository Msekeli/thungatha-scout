import hashlib
import re
from pathlib import Path

MIGRATION_FILENAME = re.compile(r"^(\d{4})-[a-z0-9-]+\.sql$")


class MigrationChecksumError(RuntimeError):
    """Raised when an already-applied migration has been modified."""


def discover_migrations(directory: Path) -> list[Path]:
    if not directory.is_dir():
        raise FileNotFoundError(f"Migration directory does not exist: {directory}")
    migrations = sorted(directory.glob("*.sql"))
    versions: set[str] = set()
    for migration in migrations:
        match = MIGRATION_FILENAME.fullmatch(migration.name)
        if match is None:
            raise ValueError(f"Invalid migration filename: {migration.name}")
        version = match.group(1)
        if version in versions:
            raise ValueError(f"Duplicate migration version: {version}")
        versions.add(version)
    return migrations


def migration_checksum(migration: Path) -> str:
    return hashlib.sha256(migration.read_bytes()).hexdigest()
