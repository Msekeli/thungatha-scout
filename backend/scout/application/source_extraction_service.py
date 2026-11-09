from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.application.source_extraction_errors import (
    SourceNotApprovedError,
    SourceNotFoundError,
    UnsupportedAdapterError,
)
from scout.application.vacancy_management_service import VacancyManagementService
from scout.ats_adapters.ats_adapter_contracts import ATSAdapter
from scout.ats_adapters.greenhouse_adapter.greenhouse_source_adapter import (
    GreenhouseSourceAdapter,
)
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository
from scout.persistence.extraction_run_repository import ExtractionRunRepository
from scout.persistence.vacancy_repository import VacancyRepository


class SourceExtractionService(VacancyManagementService):
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
        adapter_factories: dict[str, Callable[[], ATSAdapter]] | None = None,
    ) -> None:
        factory = connection_factory or get_database_connection
        super().__init__(factory)
        self._connection_factory = factory
        self._adapter_factories = (
            adapter_factories
            if adapter_factories is not None
            else {"greenhouse": GreenhouseSourceAdapter, "lever": LeverSourceAdapter}
        )

    async def extract_source(self, source_id: UUID) -> dict[str, Any]:
        with self._connection_factory() as connection:
            source = EmployerSourceRepository(connection).get_by_id(source_id)
        if source is None:
            raise SourceNotFoundError("Employer source not found.")
        if source["status"] != "verified" or source["permission_status"] != "allowed":
            raise SourceNotApprovedError(
                "Source extraction requires verified status and allowed permission."
            )
        adapter_factory = self._adapter_factories.get(source["adapter_key"])
        if adapter_factory is None:
            raise UnsupportedAdapterError("No adapter is registered for this source.")

        with self._connection_factory() as connection, connection.transaction():
            run_id = ExtractionRunRepository(connection).create(source_id)
        adapter = adapter_factory()
        result = await retrieve_adapter_result(adapter, source["adapter_config"])

        try:
            with self._connection_factory() as connection, connection.transaction():
                inserted = updated = 0
                if result.vacancies:
                    inserted, updated = VacancyRepository(connection).upsert_batch(
                        source["employer_id"],
                        source_id,
                        source["source_url"],
                        result.vacancies,
                    )
                return ExtractionRunRepository(connection).finish(
                    run_id=run_id,
                    outcome=result.outcome,
                    received=len(result.vacancies),
                    inserted=inserted,
                    updated=updated,
                    complete=result.complete,
                    detail=result.detail,
                )
        except Exception as exception:
            detail = f"Persistence failed ({type(exception).__name__}): {exception}"
            with self._connection_factory() as connection, connection.transaction():
                return ExtractionRunRepository(connection).finish(
                    run_id=run_id,
                    outcome="persistence_failure",
                    received=len(result.vacancies),
                    inserted=0,
                    updated=0,
                    complete=False,
                    detail=detail,
                )

    def list_extraction_runs(self, source_id: UUID) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            if EmployerSourceRepository(connection).get_by_id(source_id) is None:
                raise SourceNotFoundError("Employer source not found.")
            return ExtractionRunRepository(connection).list_for_source(source_id)

    def list_all_extraction_runs(self) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return ExtractionRunRepository(connection).list_latest_for_all_sources()
