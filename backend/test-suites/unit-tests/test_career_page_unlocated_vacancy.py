from uuid import uuid4

from scout.application import career_page_vacancy_persistence as vacancies
from test_career_page_vacancy_persistence import _factory, _result


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
        _factory(),
        {"employer_id": uuid4(), "source_url": "https://employer.example/careers"},
        uuid4(),
        uuid4(),
        _result(True, location=None),
    )
    assert outcome == {"outcome": "partial", "complete": False}
