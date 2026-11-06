from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.persistence.database_connection import get_database_connection
from scout.persistence.vacancy_repository import VacancyRepository


class VacancyManagementService:
    def __init__(
        self, connection_factory: Callable[[], Connection] | None = None
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection

    def get_dashboard_metrics(self) -> dict[str, int]:
        with self._connection_factory() as connection:
            return VacancyRepository(connection).get_dashboard_metrics()

    def list_vacancy_page(
        self,
        employer_id: UUID | None = None,
        location_scope: str = "south_africa",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        with self._connection_factory() as connection:
            return VacancyRepository(connection).list_page(
                employer_id=employer_id,
                location_scope=location_scope,
                limit=limit,
                offset=offset,
            )

    def export_vacancies(self, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        with self._connection_factory() as connection:
            page = VacancyRepository(connection).export_page(limit, offset)
        for vacancy in page["items"]:
            vacancy["description"] = sanitize_vacancy_description(
                vacancy.get("description")
            )
        return page

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
