from typing import Any
from uuid import UUID


class VacancyReadOperations:
    def list_page(
        self,
        employer_id: UUID | None = None,
        review_status: str | None = None,
        location_scope: str = "cape_town",
        limit: int = 50,
        offset: int = 0,
    ) -> dict[str, Any]:
        conditions = ["v.status = 'active'", "v.archived_at IS NULL"]
        parameters: list[Any] = []
        if employer_id is not None:
            conditions.append("v.employer_id = %s")
            parameters.append(employer_id)
        if review_status is not None:
            conditions.append("v.review_status = %s")
            parameters.append(review_status)
        if location_scope == "cape_town":
            conditions.append("(v.location_text ILIKE %s OR v.location_text ILIKE %s)")
            parameters.extend(["%Cape Town%", "%Stellenbosch%"])
        elif location_scope == "south_africa":
            conditions.append(
                "(v.location_text ILIKE %s OR v.location_text ILIKE %s "
                "OR v.location_text ILIKE %s)"
            )
            parameters.extend(["%South Africa%", "%Cape Town%", "%Stellenbosch%"])
        elif location_scope != "all":
            raise ValueError("Unsupported vacancy location scope.")

        where_clause = " AND ".join(conditions)
        total = self._connection.execute(
            f"""
            SELECT COUNT(*) AS total
            FROM vacancies v
            WHERE {where_clause}
            """,
            parameters,
        ).fetchone()["total"]
        items = self._connection.execute(
            f"""
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.review_status, v.review_reason, v.reviewed_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name
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

    def list_for_employer(
        self, employer_id: UUID, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.review_status, v.review_reason, v.reviewed_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name
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
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.review_status, v.review_reason, v.reviewed_at,
                   v.archived_at, v.archived_reason,
                   s.adapter_key, e.name AS employer_name
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
            SELECT v.id, v.employer_id, v.source_id, v.external_job_id,
                   v.title, v.location_text, v.department, v.office,
                   v.source_url, v.application_url, v.published_at,
                   v.source_updated_at, v.first_seen_at, v.last_seen_at,
                   v.last_checked_at, v.status, v.created_at, v.updated_at,
                   v.review_status, v.review_reason, v.reviewed_at,
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
