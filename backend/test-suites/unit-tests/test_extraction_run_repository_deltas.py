from datetime import UTC, datetime
from uuid import uuid4

from scout.persistence.extraction_run_repository import ExtractionRunRepository


class Result:
    def __init__(self, row=None, rows=None):
        self.row = row or {}
        self.rows = rows or []

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.rows


class FakeConnection:
    def __init__(self, previous, missing=()):
        self.previous = previous
        self.missing = list(missing)
        self.missing_query = ""

    def execute(self, query, parameters=None):
        if "SELECT source_id, started_at" in query:
            return Result({"source_id": uuid4(), "started_at": datetime.now(UTC)})
        if "SELECT EXISTS" in query:
            return Result({"exists": self.previous})
        if "UPDATE vacancies" in query:
            self.missing_query = query
            return Result(rows=self.missing)
        if "UPDATE extraction_runs" in query:
            return Result({"jobs_added": parameters[4],
                           "jobs_missing": parameters[5],
                           "is_baseline": parameters[6]})
        raise AssertionError(query)


def test_first_complete_run_is_baseline_not_crawler_growth():
    connection = FakeConnection(previous=False, missing=[{}, {}])
    run = ExtractionRunRepository(connection).finish(
        uuid4(), "success", 7, 7, 0, True, None
    )
    assert run == {"jobs_added": 0, "jobs_missing": 0, "is_baseline": True}
    assert not connection.missing_query


def test_later_complete_run_counts_additions_and_marks_missing_without_deleting():
    connection = FakeConnection(previous=True, missing=[{}, {}])
    run = ExtractionRunRepository(connection).finish(
        uuid4(), "success", 5, 3, 2, True, None
    )
    assert run == {"jobs_added": 3, "jobs_missing": 2, "is_baseline": False}
    assert "status = 'possibly_expired'" in connection.missing_query
    assert "archived_at IS NULL" in connection.missing_query
    assert "DELETE" not in connection.missing_query


def test_partial_run_never_marks_vacancies_missing():
    connection = FakeConnection(previous=True, missing=[{}])
    run = ExtractionRunRepository(connection).finish(
        uuid4(), "partial", 4, 2, 1, False, "Incomplete source response"
    )
    assert run["jobs_added"] == 0
    assert run["jobs_missing"] == 0
    assert not connection.missing_query
