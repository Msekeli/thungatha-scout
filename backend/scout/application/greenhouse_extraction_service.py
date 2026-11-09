from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.vacancy_management_service import VacancyManagementService
from scout.ats_adapters.greenhouse_adapter.greenhouse_adapter import GreenhouseAdapter
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository
from scout.persistence.extraction_run_repository import ExtractionRunRepository
from scout.persistence.vacancy_repository import VacancyRepository


class SourceNotFoundError(LookupError):
    """Raised when an extraction references an unknown source."""


class UnsupportedAdapterError(ValueError):
    """Raised when a source is not supported by this extraction service."""


class GreenhouseExtractionService(VacancyManagementService):
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
    ) -> None:
        factory = connection_factory or get_database_connection
        super().__init__(factory)
        self._connection_factory = factory

    async def extract_source(self, source_id: UUID) -> dict[str, Any]:
        with self._connection_factory() as connection:
            source = EmployerSourceRepository(connection).get_by_id(source_id)
        if source is None:
            raise SourceNotFoundError("Employer source not found.")
        if source["adapter_key"] != "greenhouse":
            raise UnsupportedAdapterError("This source is not a Greenhouse source.")

        token = source["adapter_config"].get("slug")
        if not isinstance(token, str) or not token.strip():
            raise UnsupportedAdapterError("Greenhouse source has no board slug.")

        with self._connection_factory() as connection, connection.transaction():
            run_id = ExtractionRunRepository(connection).create(source_id)

        adapter = GreenhouseAdapter()
        try:
            result = await adapter.retrieve(token)
        finally:
            await adapter.close()

        try:
            with self._connection_factory() as connection, connection.transaction():
                inserted = updated = 0
                if result.jobs:
                    inserted, updated = VacancyRepository(connection).upsert_batch(
                        source["employer_id"],
                        source_id,
                        source["source_url"],
                        result.jobs,
                    )
                return ExtractionRunRepository(connection).finish(
                    run_id=run_id,
                    outcome=result.outcome,
                    received=len(result.jobs),
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
                    received=len(result.jobs),
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
