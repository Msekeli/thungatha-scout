from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.career_page_observation_persistence import (
    persist_crawl_observations,
)
from scout.application.career_page_source_matching import match_existing_source
from scout.application.career_page_vacancy_persistence import (
    finish_crawl_run,
    persist_crawl_vacancies,
)
from scout.application.source_extraction_errors import SourceNotFoundError
from scout.ats_adapters.ats_adapter_contracts import ATSAdapter
from scout.crawling.career_page_crawler import CareerPageCrawler
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository
from scout.persistence.extraction_run_repository import ExtractionRunRepository


class CareerPageExtractionService:
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
        adapter_factories: dict[str, Callable[[], ATSAdapter]] | None = None,
        crawler_factory: Callable[[], CareerPageCrawler] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection
        self._adapter_factories = adapter_factories
        self._crawler_factory = crawler_factory or CareerPageCrawler

    async def extract_source(self, source_id: UUID) -> dict[str, Any]:
        with self._connection_factory() as connection:
            repository = EmployerSourceRepository(connection)
            source = repository.get_by_id(source_id)
            if source is None:
                raise SourceNotFoundError("Employer source not found.")
            sources = repository.list_for_employer(source["employer_id"])
        run_id = self._start_run(source_id)
        try:
            result = await self._crawler_factory().crawl(
                source["adapter_config"].get("start_url") or source["source_url"]
            )
            persist_crawl_observations(self._connection_factory, source_id, result)
            match = match_existing_source(sources, result.observations)
            if match:
                return await self._dispatch_existing_source(match, run_id)
            detected = next(
                (
                    page.platform_key
                    for page in result.observations
                    if page.platform_key
                ),
                None,
            )
            if detected:
                return finish_crawl_run(
                    self._connection_factory,
                    run_id,
                    "not_found",
                    f"Detected {detected}, but no matching registered source exists.",
                )
            return persist_crawl_vacancies(
                self._connection_factory, source, source_id, run_id, result
            )
        except Exception as error:
            return finish_crawl_run(
                self._connection_factory,
                run_id,
                "transient_failure",
                f"Crawl failed ({type(error).__name__}).",
            )

    def _start_run(self, source_id: UUID) -> UUID:
        with self._connection_factory() as connection, connection.transaction():
            return ExtractionRunRepository(connection).create(source_id)

    async def _dispatch_existing_source(
        self, source: dict, run_id: UUID
    ) -> dict[str, Any]:
        finish_crawl_run(
            self._connection_factory,
            run_id,
            "success",
            f"Matched registered {source['adapter_key']} source; delegated extraction.",
            True,
        )
        from scout.application.source_extraction_service import SourceExtractionService

        return await SourceExtractionService(
            self._connection_factory, self._adapter_factories
        ).extract_source(source["id"])
