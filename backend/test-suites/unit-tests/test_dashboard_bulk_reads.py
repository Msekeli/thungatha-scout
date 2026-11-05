from scout.application.employer_service import EmployerService
from scout.application.greenhouse_extraction_service import GreenhouseExtractionService
from dashboard_bulk_read_test_connection import FakeConnection


def test_employer_sources_are_loaded_with_one_bulk_query() -> None:
    rows = [{"id": "source-1"}, {"id": "source-2"}]
    connection = FakeConnection(rows)
    service = EmployerService(connection_factory=lambda: connection)

    result = service.list_all_sources()

    assert result == rows
    assert len(connection.queries) == 1
    assert "ORDER BY employer_id, created_at, id" in connection.queries[0][0]


def test_extraction_history_is_loaded_for_all_sources_in_one_query() -> None:
    rows = [{"source_id": "source-1", "outcome": "success"}]
    connection = FakeConnection(rows)
    service = GreenhouseExtractionService(connection_factory=lambda: connection)

    result = service.list_all_extraction_runs()

    query = connection.queries[0][0]
    assert result == rows
    assert len(connection.queries) == 1
    assert "PARTITION BY source_id" in query
    assert "source_rank <= 20" in query
