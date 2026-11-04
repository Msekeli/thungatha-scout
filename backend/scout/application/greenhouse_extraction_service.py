from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.greenhouse_adapter import GreenhouseAdapter
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository
from scout.persistence.extraction_run_repository import ExtractionRunRepository
from scout.persistence.vacancy_repository import VacancyRepository


class SourceNotFoundError(LookupError):
    """Raised when an extraction references an unknown source."""


class UnsupportedAdapterError(ValueError):
    """Raised when a source is not supported by this extraction service."""


class GreenhouseExtractionService:
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection

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

    def list_vacancies(
        self, employer_id: UUID | None = None, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            repository = VacancyRepository(connection)
            if employer_id is not None:
                return repository.list_for_employer(employer_id, limit, offset)
            return repository.list_all(limit, offset)
