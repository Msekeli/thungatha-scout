from collections.abc import Callable
from typing import Any, Literal
from uuid import UUID

from psycopg.connection import Connection
from pydantic import BaseModel, ConfigDict, Field, HttpUrl

from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_source_repository import EmployerSourceRepository


class EmployerSourceUpdate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    adapter_key: Literal["greenhouse", "workday"]
    source_url: HttpUrl
    normalized_url: HttpUrl
    adapter_config: dict[str, Any] = Field(default_factory=dict)


class EmployerSourceUpdateService:
    def __init__(
        self,
        connection_factory: Callable[[], Connection] | None = None,
    ) -> None:
        self._connection_factory = connection_factory or get_database_connection

    def update_configuration(
        self,
        employer_id: UUID,
        source_id: UUID,
        payload: EmployerSourceUpdate,
    ) -> dict[str, Any] | None:
        values = payload.model_dump()
        values["source_url"] = str(values["source_url"])
        values["normalized_url"] = str(values["normalized_url"])
        with self._connection_factory() as connection, connection.transaction():
            return EmployerSourceRepository(connection).update_configuration(
                employer_id,
                source_id,
                values,
            )
