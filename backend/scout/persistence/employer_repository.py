from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection
from psycopg.types.json import Jsonb


class EmployerRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, values: Mapping[str, Any]) -> dict[str, Any]:
        row = self._connection.execute(
            """
            INSERT INTO employers (name, legal_name, website_url, organization_type, status, city, province, country, identity_evidence, location_evidence)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) RETURNING *
            """,
            (values["name"], values.get("legal_name"), values.get("website_url"), values["organization_type"], values["status"], values.get("city"), values.get("province"), values.get("country"), Jsonb(values.get("identity_evidence", [])), Jsonb(values.get("location_evidence", []))),
        ).fetchone()
        return row

    def get_by_id(self, employer_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute("SELECT * FROM employers WHERE id = %s", (employer_id,)).fetchone()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            "SELECT * FROM employers ORDER BY created_at DESC, id LIMIT %s OFFSET %s",
            (limit, offset),
        ).fetchall()

    def update_details(self, employer_id: UUID, values: Mapping[str, Any]) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employers SET name = %s, legal_name = %s, website_url = %s,
                organization_type = %s, updated_at = NOW()
            WHERE id = %s RETURNING *
            """,
            (values["name"], values.get("legal_name"), values.get("website_url"), values["organization_type"], employer_id),
        ).fetchone()

    def update_branding(self, employer_id: UUID, logo_url: str | None, logo_source_url: str | None) -> dict[str, Any] | None:
        return self._connection.execute(
            "UPDATE employers SET logo_url = %s, logo_source_url = %s, updated_at = NOW() WHERE id = %s RETURNING *",
            (logo_url, logo_source_url, employer_id),
        ).fetchone()

    def update_status(self, employer_id: UUID, status: str) -> dict[str, Any] | None:
        return self._connection.execute(
            "UPDATE employers SET status = %s, updated_at = NOW() WHERE id = %s RETURNING *",
            (status, employer_id),
        ).fetchone()

    def delete(self, employer_id: UUID) -> bool:
        self._connection.execute(
            "DELETE FROM extraction_runs WHERE source_id IN "
            "(SELECT id FROM employer_sources WHERE employer_id = %s)",
            (employer_id,),
        )
        self._connection.execute("DELETE FROM vacancies WHERE employer_id = %s", (employer_id,))
        self._connection.execute("DELETE FROM employer_sources WHERE employer_id = %s", (employer_id,))
        cursor = self._connection.execute("DELETE FROM employers WHERE id = %s", (employer_id,))
        return cursor.rowcount > 0
