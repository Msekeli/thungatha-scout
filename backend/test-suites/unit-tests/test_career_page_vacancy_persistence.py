from contextlib import contextmanager
from types import SimpleNamespace
from uuid import uuid4

from scout.application import career_page_vacancy_persistence as vacancies


class _Connection:
    def transaction(self):
        return _Transaction()


class _Transaction:
    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _factory():
    @contextmanager
    def open_connection():
        yield _Connection()
    return open_connection


def _result(complete, failed=(), location="Cape Town"):
    vacancy = SimpleNamespace(
        external_job_id="job-1",
        title="Software Developer",
        application_url="https://employer.example/jobs/1",
        location_text=location,
    )
    page = SimpleNamespace(outcome="success", vacancies=(vacancy,))
    return SimpleNamespace(
        observations=(page,), complete=complete, failed_urls=failed,
        skipped_urls=(), vacancies=(vacancy,), detail=None,
    )


def test_partial_crawl_persists_found_jobs_without_marking_complete(monkeypatch):
    captured = {}

    class VacancyStore:
        def __init__(self, connection):
            pass

        def upsert_batch(self, employer_id, source_id, source_url, items):
            captured["upserted"] = items
            return 1, 0

    class RunStore:
        def __init__(self, connection):
            pass

        def finish(self, *args):
            return {"outcome": args[1], "complete": args[5]}

    monkeypatch.setattr(vacancies, "VacancyRepository", VacancyStore)
    monkeypatch.setattr(vacancies, "ExtractionRunRepository", RunStore)
    result = _result(False, failed=("https://employer.example/jobs",))
    outcome = vacancies.persist_crawl_vacancies(
        _factory(), {"employer_id": uuid4(), "source_url": "https://employer.example/careers"},
        uuid4(), uuid4(), result,
    )
    assert len(captured["upserted"]) == 1
    assert outcome == {"outcome": "partial", "complete": False}


def test_unlocated_vacancy_is_withheld_and_run_stays_partial(monkeypatch):
    class VacancyStore:
        def __init__(self, connection):
            pass

        def upsert_batch(self, *args):
            raise AssertionError("Unlocated vacancies must not be persisted.")

    class RunStore:
        def __init__(self, connection):
            pass

        def finish(self, *args):
            return {"outcome": args[1], "complete": args[5]}

    monkeypatch.setattr(vacancies, "VacancyRepository", VacancyStore)
    monkeypatch.setattr(vacancies, "ExtractionRunRepository", RunStore)
    outcome = vacancies.persist_crawl_vacancies(
        _factory(), {"employer_id": uuid4(), "source_url": "https://employer.example/careers"},
        uuid4(), uuid4(), _result(True, location=None),
    )
    assert outcome == {"outcome": "partial", "complete": False}
