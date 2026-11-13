from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.crawling.career_page_observation import CareerPageCrawlResult
from scout.persistence.extraction_run_repository import ExtractionRunRepository
from scout.persistence.vacancy_repository import VacancyRepository


def persist_crawl_vacancies(
    factory: Callable[[], Connection],
    source: dict,
    source_id: UUID,
    run_id: UUID,
    result: CareerPageCrawlResult,
) -> dict[str, Any]:
    complete = result.complete and not result.failed_urls and not result.skipped_urls
    complete = complete and all(
        page.outcome == "success" for page in result.observations
    )
    vacancies = list(result.vacancies)
    located = [
        item for item in vacancies
        if item.location_text and item.location_text.strip()
    ]
    if len(located) != len(vacancies):
        complete = False
    outcome = ("success" if located else "empty") if complete else "partial"
    detail = result.detail
    if not complete and not detail:
        detail = "Crawl was partial or included vacancies without a location."
    with factory() as connection, connection.transaction():
        inserted, updated = (0, 0)
        if located:
            inserted, updated = VacancyRepository(connection).upsert_batch(
                source["employer_id"], source_id, source["source_url"], located
            )
        return ExtractionRunRepository(connection).finish(
            run_id, outcome, len(located), inserted, updated, complete, detail
        )


def finish_crawl_run(
    factory: Callable[[], Connection],
    run_id: UUID,
    outcome: str,
    detail: str,
    complete: bool = False,
) -> dict[str, Any]:
    with factory() as connection, connection.transaction():
        return ExtractionRunRepository(connection).finish(
            run_id, outcome, 0, 0, 0, complete, detail
        )
