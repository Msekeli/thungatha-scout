from contextlib import contextmanager
from datetime import UTC, datetime
from types import SimpleNamespace
from uuid import uuid4

from scout.application import career_page_observation_persistence as observations


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


def test_preview_retains_completeness_and_page_evidence(monkeypatch):
    captured = {}

    class Repository:
        def __init__(self, connection):
            pass

        def update_discovery_preview(self, source_id, preview):
            captured.update(preview)

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
        vacancies=(),
    )
    result = SimpleNamespace(
        observations=(page,),
        complete=False,
        failed_urls=(),
        skipped_urls=("https://employer.example/jobs",),
        vacancies=(),
    )
    monkeypatch.setattr(observations, "EmployerSourceRepository", Repository)
    observations.persist_crawl_observations(_factory(), uuid4(), result)
    assert captured["crawl_complete"] is False
    assert captured["pages_observed"] == 1
    assert captured["pages"][0]["status_code"] == 200
    assert captured["skipped_urls"] == ["https://employer.example/jobs"]
