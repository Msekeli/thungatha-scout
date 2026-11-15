from typing import Any
from uuid import UUID

from scout.persistence.vacancy_location_scope import location_scope_condition


AGE_FILTERS = {
    "new": "v.first_seen_at >= NOW() - INTERVAL '24 hours'",
    "old": "COALESCE(v.source_updated_at, v.published_at) < NOW() - INTERVAL '8 days'",
    "8_14": "COALESCE(v.source_updated_at, v.published_at) < NOW() - INTERVAL '7 days' AND COALESCE(v.source_updated_at, v.published_at) >= NOW() - INTERVAL '15 days'",
    "15_30": "COALESCE(v.source_updated_at, v.published_at) < NOW() - INTERVAL '14 days' AND COALESCE(v.source_updated_at, v.published_at) >= NOW() - INTERVAL '31 days'",
    "over_30": "COALESCE(v.source_updated_at, v.published_at) < NOW() - INTERVAL '30 days'",
    "undated": "v.source_updated_at IS NULL AND v.published_at IS NULL",
}


class VacancyPageReadOperations:
    def list_page(
        self,
        employer_id: UUID | None = None,
        location_scope: str = "south_africa",
        limit: int = 50,
        offset: int = 0,
        age_filter: str = "all",
    ) -> dict[str, Any]:
        conditions = ["v.status = 'active'", "v.archived_at IS NULL"]
        parameters: list[Any] = []
        if employer_id is not None:
            conditions.append("v.employer_id = %s")
            parameters.append(employer_id)
        location, location_values = location_scope_condition(location_scope)
        if location:
            conditions.append(location)
            parameters.extend(location_values)
        if age_filter not in ("all", *AGE_FILTERS):
            raise ValueError("Unsupported vacancy age filter.")
        if age_filter != "all":
            conditions.append(AGE_FILTERS[age_filter])
        where = " AND ".join(conditions)
        total = self._connection.execute(
            f"SELECT COUNT(*) AS total FROM vacancies v WHERE {where}", parameters
        ).fetchone()["total"]
        items = self._read_items(where, parameters, limit, offset)
        return {
            "items": items,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(items) < total,
        }

    def _read_items(
        self, where: str, values: list[Any], limit: int, offset: int
    ) -> list[dict[str, Any]]:
        return self._connection.execute(
            f"""
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.archived_at, v.archived_reason, s.adapter_key,
                   e.name AS employer_name, e.website_url AS employer_website_url,
                   s.employer_careers_url, e.logo_url AS employer_logo_url,
                   e.logo_source_url AS employer_logo_source_url,
                   e.logo_type AS employer_logo_type
            FROM vacancies v JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE {where}
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            [*values, limit, offset],
        ).fetchall()
