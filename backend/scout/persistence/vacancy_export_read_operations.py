from typing import Any

from scout.persistence.vacancy_location_scope import location_scope_condition


class VacancyExportReadOperations:
    def export_page(
        self, limit: int, offset: int, location_scope: str = "south_africa"
    ) -> dict[str, Any]:
        where = "v.status = 'active' AND v.archived_at IS NULL"
        location_condition, parameters = location_scope_condition(location_scope)
        if location_condition:
            where += f" AND {location_condition}"
        joins = """
            FROM vacancies v
            JOIN employers e ON e.id = v.employer_id
            JOIN employer_sources s ON s.id = v.source_id
        """
        total = self._connection.execute(
            f"SELECT COUNT(*) AS total {joins} WHERE {where}", parameters
        ).fetchone()["total"]
        rows = self._connection.execute(
            f"""
            SELECT v.id AS scout_vacancy_id, v.source_id AS scout_source_id,
                   v.external_job_id,
                   'scout_source_' || replace(s.id::text, '-', '') AS provider_key,
                   s.adapter_key AS provider_kind, e.name AS employer_name,
                   e.logo_url, e.logo_source_url,
                   v.title, v.description, v.location_text, v.department,
                   v.office, v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.content_fingerprint
            {joins}
            WHERE {where}
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            [*parameters, limit, offset],
        ).fetchall()
        return {
            "items": rows,
            "total": total,
            "limit": limit,
            "offset": offset,
            "has_more": offset + len(rows) < total,
        }
