import os
from uuid import uuid4

import pytest

from scout.application.employer_service import (
    EmployerCreate,
    EmployerService,
    EmployerSourceCreate,
)
from scout.persistence.database_connection import get_database_connection
from scout.persistence.migration_runner import run_migrations

pytestmark = pytest.mark.skipif(
    os.getenv("SCOUT_RUN_DATABASE_INTEGRATION_TESTS") != "true",
    reason="Set SCOUT_RUN_DATABASE_INTEGRATION_TESTS=true to use Scout Supabase.",
)


def test_supabase_employer_and_source_persistence_round_trip() -> None:
    applied_versions = run_migrations()
    assert isinstance(applied_versions, list)

    service = EmployerService()
    employer = service.create_employer(
        EmployerCreate(
            name=f"Scout persistence test {uuid4()}",
            city="Cape Town",
            province="Western Cape",
            country="South Africa",
            identity_evidence=[{"type": "test", "url": "https://example.com"}],
            location_evidence=[{"type": "test", "url": "https://example.com"}],
        )
    )
    assert employer["status"] == "discovered"
    source_id = None

    try:
        source = service.create_source(
            EmployerSourceCreate(
                employer_id=employer["id"],
                adapter_key="greenhouse",
                source_url="https://boards.greenhouse.io/example",
                employer_careers_url="https://example.com/careers",
                normalized_url=f"https://boards.greenhouse.io/example-{uuid4()}",
                relationship_evidence=[
                    {"type": "test", "url": "https://example.com/careers"}
                ],
            )
        )
        source_id = source["id"]
        assert source["status"] == "discovered"
        assert source["permission_status"] == "unknown"

        assert service.get_employer(employer["id"])["id"] == employer["id"]
        assert service.list_sources(employer["id"])[0]["id"] == source_id
    finally:
        with get_database_connection() as connection:
            if source_id is not None:
                connection.execute(
                    "DELETE FROM employer_sources WHERE id = %s",
                    (source_id,),
                )
            connection.execute(
                "DELETE FROM employers WHERE id = %s",
                (employer["id"],),
            )
