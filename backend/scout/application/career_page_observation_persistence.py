from collections.abc import Callable
from uuid import UUID

from psycopg.connection import Connection

from scout.crawling.career_page_observation import CareerPageCrawlResult
from scout.persistence.employer_source_repository import EmployerSourceRepository


def persist_crawl_observations(
    factory: Callable[[], Connection],
    source_id: UUID,
    result: CareerPageCrawlResult,
) -> None:
    pages = [
        {
            "requested_url": page.requested_url,
            "final_url": page.final_url,
            "canonical_url": page.canonical_url,
            "status_code": page.status_code,
            "content_type": page.content_type,
            "page_title": page.page_title,
            "platform_key": page.platform_key,
            "observed_at": page.observed_at.isoformat(),
            "outcome": page.outcome,
            "discovered_links": list(page.discovered_links[:20]),
            "vacancies_found": len(page.vacancies),
        }
        for page in result.observations
    ]
    preview = {
        "crawl_complete": result.complete,
        "pages_observed": len(pages),
        "vacancies_found": len(result.vacancies),
        "total_vacancies": len(result.vacancies),
        "jobs": [
            {
                "id": item.external_job_id,
                "title": item.title,
                "absolute_url": item.application_url,
                "location": {"name": item.location_text},
            }
            for item in result.vacancies[:5]
        ],
        "failed_urls": list(result.failed_urls[:20]),
        "skipped_urls": list(result.skipped_urls[:20]),
        "pages": pages,
    }
    with factory() as connection, connection.transaction():
        EmployerSourceRepository(connection).update_discovery_preview(
            source_id, preview
        )
