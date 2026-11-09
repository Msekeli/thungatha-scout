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
            SELECT v.id AS scout_vacancy_id, e.name AS employer_name,
                   e.logo_url, v.title, v.description, v.location_text,
                   v.application_url, v.published_at, v.source_updated_at,
                   v.first_seen_at
            {joins}
            WHERE {where}
            ORDER BY v.published_at DESC NULLS LAST,
                     v.source_updated_at DESC NULLS LAST,
                     v.created_at DESC, v.id ASC
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
            "location_scope": location_scope,
        }
