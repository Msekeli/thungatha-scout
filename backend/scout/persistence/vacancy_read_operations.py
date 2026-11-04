from typing import Any
from uuid import UUID


class VacancyReadOperations:
    def list_for_employer(
        self, employer_id: UUID, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.employer_id = %s AND v.status = 'active'
              AND v.archived_at IS NULL
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (employer_id, limit, offset),
        ).fetchall()

    def list_all(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.status = 'active' AND v.archived_at IS NULL
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()

    def get_by_id(self, vacancy_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name,
                   e.logo_url AS employer_logo_url,
                   e.logo_source_url AS employer_logo_source_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.id = %s
            """,
            (vacancy_id,),
        ).fetchone()

    def list_archived(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name,
                   e.logo_url AS employer_logo_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.archived_at IS NOT NULL
            ORDER BY v.archived_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()
