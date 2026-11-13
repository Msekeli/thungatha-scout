from contextlib import contextmanager
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from scout.application import career_page_observation_persistence as observations
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


def _vacancy(location="Cape Town"):
    return SimpleNamespace(
        external_job_id="job-1",
        title="Software Developer",
        application_url="https://employer.example/jobs/1",
        location_text=location,
    )


def _result(complete, failed=(), skipped=(), location="Cape Town"):
    page = SimpleNamespace(
        requested_url="https://employer.example/careers",
        final_url="https://employer.example/careers",
        canonical_url=None,
        status_code=200,
        content_type="text/html",
        page_title="Careers",
        platform_key=None,
        observed_at=datetime.now(UTC),
        outcome="success",
        discovered_links=("https://employer.example/jobs",),
        vacancies=(_vacancy(location),),
    )
    return SimpleNamespace(
        observations=(page,),
        complete=complete,
        failed_urls=failed,
        skipped_urls=skipped,
        vacancies=(page.vacancies[0],),
        detail=None,
    )


def test_observation_preview_retains_completeness_and_page_evidence(monkeypatch):
    captured = {}

    class Repository:
        def __init__(self, connection):
            pass

        def update_discovery_preview(self, source_id, preview):
            captured.update(preview)

    monkeypatch.setattr(observations, "EmployerSourceRepository", Repository)
    observations.persist_crawl_observations(_factory(), uuid4(), _result(False, skipped=("https://employer.example/jobs",)))
    assert captured["crawl_complete"] is False
    assert captured["pages_observed"] == 1
    assert captured["pages"][0]["status_code"] == 200
    assert captured["skipped_urls"] == ["https://employer.example/jobs"]


def test_partial_crawl_upserts_found_jobs_but_finishes_incomplete(monkeypatch):
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
            captured["finish"] = args
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


def test_vacancy_without_location_keeps_run_partial(monkeypatch):
    captured = {}

    class VacancyStore:
        def __init__(self, connection):
            pass

        def upsert_batch(self, *args):
            raise AssertionError("Unlocated vacancies must not be persisted.")

    class RunStore:
        def __init__(self, connection):
            pass

        def finish(self, *args):
            captured["finish"] = args
            return {"outcome": args[1], "complete": args[5]}

    monkeypatch.setattr(vacancies, "VacancyRepository", VacancyStore)
    monkeypatch.setattr(vacancies, "ExtractionRunRepository", RunStore)
    outcome = vacancies.persist_crawl_vacancies(
        _factory(), {"employer_id": uuid4(), "source_url": "https://employer.example/careers"},
        uuid4(), uuid4(), _result(True, location=None),
    )
    assert outcome == {"outcome": "partial", "complete": False}
    assert captured["finish"][2] == 0
