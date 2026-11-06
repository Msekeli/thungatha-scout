from typing import Any
from uuid import UUID


class VacancyArchiveOperations:
    def archive(
        self, vacancy_id: UUID, reason: str | None = None
    ) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            UPDATE vacancies
            SET archived_at = NOW(), archived_reason = %s, updated_at = NOW()
            WHERE id = %s AND archived_at IS NULL
            RETURNING id
            """,
            (reason, vacancy_id),
        ).fetchone()
        return self.get_by_id(vacancy_id) if row else None

    def restore(self, vacancy_id: UUID) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            UPDATE vacancies
            SET archived_at = NULL, archived_reason = NULL, updated_at = NOW()
            WHERE id = %s AND archived_at IS NOT NULL
            RETURNING id
            """,
            (vacancy_id,),
        ).fetchone()
        return self.get_by_id(vacancy_id) if row else None

    def list_archived(
        self, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name,
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
