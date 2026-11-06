from typing import Any
from uuid import UUID


class VacancyCollectionReadOperations:
    def list_for_employer(
        self, employer_id: UUID, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._list_active(employer_id, limit, offset)

    def list_all(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        return self._list_active(None, limit, offset)

    def _list_active(
        self, employer_id: UUID | None, limit: int, offset: int
    ) -> list[dict[str, Any]]:
        has_employer_filter = employer_id is not None
        employer_filter = " AND v.employer_id = %s" if has_employer_filter else ""
        parameters: list[Any] = [employer_id] if has_employer_filter else []
        parameters.extend((limit, offset))
        return self._connection.execute(
            f"""
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.status = 'active' AND v.archived_at IS NULL
              {employer_filter}
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            parameters,
        ).fetchall()
