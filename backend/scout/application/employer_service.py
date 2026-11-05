from collections.abc import Callable
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.application.employer_contracts import (
    EmployerBrandingUpdate,
    EmployerCreate,
    EmployerSourceCreate,
)
from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_repository import EmployerRepository
from scout.persistence.employer_source_repository import EmployerSourceRepository


class EmployerService:
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection

    def create_employer(self, payload: EmployerCreate) -> dict[str, Any]:
        values = payload.model_dump()
        values["status"] = "discovered"
        if values["website_url"] is not None:
            values["website_url"] = str(values["website_url"])

        with self._connection_factory() as connection, connection.transaction():
            return EmployerRepository(connection).create(values)

    def list_employers(
        self,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return EmployerRepository(connection).list_all(
                limit=limit,
                offset=offset,
            )

    def get_employer(self, employer_id: UUID) -> dict[str, Any] | None:
        with self._connection_factory() as connection:
            return EmployerRepository(connection).get_by_id(employer_id)

    def update_status(self, employer_id: UUID, status: str) -> dict[str, Any] | None:
        with self._connection_factory() as connection, connection.transaction():
            return EmployerRepository(connection).update_status(employer_id, status)

    def delete_employer(self, employer_id: UUID) -> bool:
        with self._connection_factory() as connection, connection.transaction():
            return EmployerRepository(connection).delete(employer_id)

    def update_branding(
        self, employer_id: UUID, payload: EmployerBrandingUpdate
    ) -> dict[str, Any] | None:
        values = payload.model_dump()
        for key in ("logo_url", "logo_source_url"):
            if values[key] is not None:
                values[key] = str(values[key])
        with self._connection_factory() as connection, connection.transaction():
            return EmployerRepository(connection).update_branding(
                employer_id, values["logo_url"], values["logo_source_url"]
            )

    def create_source(self, payload: EmployerSourceCreate) -> dict[str, Any]:
        values = payload.model_dump()
        values["status"] = "discovered"
        values["permission_status"] = "unknown"
        values["source_url"] = str(values["source_url"])
        if values["employer_careers_url"] is not None:
            values["employer_careers_url"] = str(values["employer_careers_url"])
        values["normalized_url"] = str(values["normalized_url"])

        with self._connection_factory() as connection, connection.transaction():
            return EmployerSourceRepository(connection).create(values)

    def list_sources(self, employer_id: UUID) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return EmployerSourceRepository(connection).list_for_employer(employer_id)

    def list_all_sources(self) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return EmployerSourceRepository(connection).list_all()
