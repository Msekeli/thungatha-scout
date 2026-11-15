from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.persistence.employer_delete_operations import EmployerDeleteOperations
from scout.persistence.employer_details_update_operations import (
    EmployerDetailsUpdateOperations,
)


class EmployerRepository(EmployerDeleteOperations, EmployerDetailsUpdateOperations):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, values: Mapping[str, Any]) -> dict[str, Any]:
        return self._connection.execute(
            """
            INSERT INTO employers (
                name, legal_name, website_url, logo_url, logo_source_url, logo_type,
                organization_type, city, province, country
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                values["name"],
                values.get("legal_name"),
                values.get("website_url"),
                values.get("logo_url"),
                values.get("logo_source_url"),
                values.get("logo_type", "unverified"),
                values["organization_type"],
                values.get("city"),
                values.get("province"),
                values.get("country"),
            ),
        ).fetchone()

    def get_by_id(self, employer_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute(
            "SELECT * FROM employers WHERE id = %s", (employer_id,)
        ).fetchone()

    def list_all(self, limit: int = 100, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT e.*,
                   COUNT(v.id) FILTER (
                       WHERE v.status = 'active' AND v.archived_at IS NULL
                   )::INTEGER AS vacancy_count
            FROM employers e
            LEFT JOIN vacancies v ON v.employer_id = e.id
            GROUP BY e.id
            ORDER BY e.created_at DESC, e.id
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

    def update_branding(
        self,
        employer_id: UUID,
        logo_url: str | None,
        logo_source_url: str | None,
        logo_type: str,
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employers SET logo_url = %s, logo_source_url = %s, logo_type = %s, updated_at = NOW()
            WHERE id = %s RETURNING *
            """,
            (logo_url, logo_source_url, logo_type, employer_id),
        ).fetchone()

    def update_branding_if_unusable(
        self,
        employer_id: UUID,
        expected_logo_url: str | None,
        logo_url: str,
        logo_source_url: str,
        logo_type: str,
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employers
            SET logo_url = %s, logo_source_url = %s, logo_type = %s, updated_at = NOW()
            WHERE id = %s AND logo_url IS NOT DISTINCT FROM %s
            RETURNING *
            """,
            (logo_url, logo_source_url, logo_type, employer_id, expected_logo_url),
        ).fetchone()
