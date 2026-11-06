from typing import Any
from uuid import UUID

from scout.persistence.vacancy_location_scope import location_scope_condition


class VacancyPageReadOperations:
    def list_page(
        self,
        employer_id: UUID | None = None,
        location_scope: str = "south_africa",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        conditions = ["v.status = 'active'", "v.archived_at IS NULL"]
        parameters: list[Any] = []
        if employer_id is not None:
            conditions.append("v.employer_id = %s")
            parameters.append(employer_id)
        location_condition, location_parameters = location_scope_condition(
            location_scope
        )
        if location_condition:
            conditions.append(location_condition)
            parameters.extend(location_parameters)
        where_clause = " AND ".join(conditions)
        total = self._connection.execute(
            f"SELECT COUNT(*) AS total FROM vacancies v WHERE {where_clause}",
            parameters,
        ).fetchone()["total"]
        items = self._connection.execute(
            f"""
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name,
                   s.employer_careers_url AS employer_careers_url,
                   e.logo_url AS employer_logo_url,
                   e.logo_source_url AS employer_logo_source_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE {where_clause}
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            [*parameters, limit, offset],
        ).fetchall()
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(items) < total,
        }
