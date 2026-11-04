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

    def list_vacancies(
        self, employer_id: UUID | None = None, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            repository = VacancyRepository(connection)
            if employer_id is not None:
                return repository.list_for_employer(employer_id, limit, offset)
            return repository.list_all(limit, offset)

    def get_vacancy(self, vacancy_id: UUID) -> dict[str, Any] | None:
        with self._connection_factory() as connection:
            return VacancyRepository(connection).get_by_id(vacancy_id)

    def update_vacancy_review(
        self, vacancy_id: UUID, review_status: str, review_reason: str | None
    ) -> dict[str, Any] | None:
        with self._connection_factory() as connection, connection.transaction():
            return VacancyRepository(connection).update_review(
                vacancy_id, review_status, review_reason
            )

    def archive_vacancy(
        self, vacancy_id: UUID, reason: str | None = None
    ) -> dict[str, Any] | None:
        with self._connection_factory() as connection, connection.transaction():
            return VacancyRepository(connection).archive(vacancy_id, reason)

    def restore_vacancy(self, vacancy_id: UUID) -> dict[str, Any] | None:
        with self._connection_factory() as connection, connection.transaction():
            return VacancyRepository(connection).restore(vacancy_id)

    def list_archived_vacancies(
        self, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return VacancyRepository(connection).list_archived(limit, offset)
