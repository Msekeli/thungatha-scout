from typing import Any, Callable, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, HttpUrl
from psycopg.connection import Connection

from scout.persistence.database_connection import get_database_connection
from scout.persistence.employer_repository import EmployerRepository
from scout.persistence.employer_source_repository import EmployerSourceRepository


OrganizationType = Literal[
    "direct_employer",
    "recruitment_agency",
    "staffing_company",
    "hybrid",
    "other",
    "unresolved",
]


class EmployerCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1)
    legal_name: str | None = None
    website_url: HttpUrl | None = None
    organization_type: OrganizationType = "unresolved"
    city: str | None = None
    province: str | None = None
    country: str | None = None
    identity_evidence: list[dict[str, Any]] = Field(default_factory=list)
    location_evidence: list[dict[str, Any]] = Field(default_factory=list)


class EmployerSourceCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    employer_id: UUID
    adapter_key: Literal["greenhouse", "workday"]
    source_url: HttpUrl
    employer_careers_url: HttpUrl | None = None
    normalized_url: HttpUrl
    adapter_config: dict[str, Any] = Field(default_factory=dict)
    relationship_evidence: list[dict[str, Any]] = Field(default_factory=list)


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

        with self._connection_factory() as connection:
            with connection.transaction():
                return EmployerRepository(connection).create(values)

    def get_employer(self, employer_id: UUID) -> dict[str, Any] | None:
        with self._connection_factory() as connection:
            return EmployerRepository(connection).get_by_id(employer_id)

    def create_source(self, payload: EmployerSourceCreate) -> dict[str, Any]:
        values = payload.model_dump()
        values["status"] = "discovered"
        values["permission_status"] = "unknown"
        values["source_url"] = str(values["source_url"])
        if values["employer_careers_url"] is not None:
            values["employer_careers_url"] = str(
                values["employer_careers_url"]
            )
        values["normalized_url"] = str(values["normalized_url"])

        with self._connection_factory() as connection:
            with connection.transaction():
                return EmployerSourceRepository(connection).create(values)

    def list_sources(self, employer_id: UUID) -> list[dict[str, Any]]:
        with self._connection_factory() as connection:
            return EmployerSourceRepository(connection).list_for_employer(
                employer_id
            )
