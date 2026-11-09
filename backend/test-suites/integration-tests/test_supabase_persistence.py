import os
from uuid import uuid4

import pytest

from scout.application.employer_service import EmployerService
from scout.application.employer_contracts import EmployerCreate, EmployerSourceCreate
from scout.persistence.database_connection import get_database_connection
from scout.persistence.migration_runner import run_migrations

pytestmark = pytest.mark.skipif(
    os.getenv("SCOUT_RUN_DATABASE_INTEGRATION_TESTS") != "true",
    reason="Set SCOUT_RUN_DATABASE_INTEGRATION_TESTS=true to use Scout Supabase.",
)


def test_supabase_employer_and_source_persistence_round_trip() -> None:
    assert isinstance(run_migrations(), list)
    service = EmployerService()
    employer = service.create_employer(EmployerCreate(name=f"Scout persistence test {uuid4()}"))
    source_id = None
    try:
        source = service.create_source(EmployerSourceCreate(
            employer_id=employer["id"], adapter_key="greenhouse",
            source_url="https://boards.greenhouse.io/example",
            employer_careers_url="https://example.com/careers",
            normalized_url=f"https://boards.greenhouse.io/example-{uuid4()}",
            adapter_config={"slug": "example"},
        ))
        source_id = source["id"]
        assert "status" not in source
        assert "permission_status" not in source
        assert service.get_employer(employer["id"])["id"] == employer["id"]
        assert service.list_sources(employer["id"])[0]["id"] == source_id
    finally:
        with get_database_connection() as connection:
            if source_id is not None:
                connection.execute("DELETE FROM employer_sources WHERE id = %s", (source_id,))
            connection.execute("DELETE FROM employers WHERE id = %s", (employer["id"],))
