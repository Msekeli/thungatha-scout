from typing import Any
from uuid import UUID


class VacancyReadOperations:
    def get_dashboard_metrics(self) -> dict[str, int]:
        row = self._connection.execute(
            """
            SELECT
                COUNT(*) FILTER (
                    WHERE status = 'active' AND archived_at IS NULL
                ) AS total_active,
                COUNT(*) FILTER (
                    WHERE status = 'active' AND archived_at IS NULL
                      AND first_seen_at >= NOW() - INTERVAL '24 hours'
                ) AS new_last_24_hours
            FROM vacancies
            """
        ).fetchone()
        return {
            "total_active": row["total_active"],
            "new_last_24_hours": row["new_last_24_hours"],
        }

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
        if location_scope in {"cape_town", "western_cape", "south_africa"}:
            normalized_location = (
                "regexp_replace(lower(coalesce(v.location_text, '')), "
                "'[^a-z0-9]+', ' ', 'g')"
            )
            terms = {
                "cape_town": (
                    "cape town", "ct", "cpt", "durbanville", "bellville",
                    "brackenfell", "kraaifontein", "kuils river", "parow",
                    "goodwood", "milnerton", "century city", "table view",
                    "blouberg", "camps bay", "sea point", "claremont",
                    "rondebosch", "wynberg", "plumstead", "tokai", "hout bay",
                    "fish hoek", "muizenberg", "simons town", "noordhoek",
                    "khayelitsha", "mitchells plain", "somerset west", "gordons bay",
                ),
                "western_cape": (
                    "western cape", "wc", "cape town", "ct", "cpt", "stellenbosch",
                    "durbanville", "bellville", "brackenfell", "kraaifontein",
                    "kuils river", "parow", "goodwood", "milnerton", "century city",
                    "table view", "blouberg", "camps bay", "sea point", "claremont",
                    "rondebosch", "wynberg", "plumstead", "tokai", "hout bay",
                    "fish hoek", "muizenberg", "simons town", "noordhoek",
                    "khayelitsha", "mitchells plain", "somerset west", "gordons bay",
                    "paarl", "wellington", "franschhoek", "worcester", "george",
                    "mossel bay", "oudtshoorn", "knysna", "hermanus", "malmesbury",
                    "saldanha",
                ),
                "south_africa": (
                    "south africa", "sa", "za", "zaf", "western cape", "wc",
                    "eastern cape", "ec", "free state", "fs", "gauteng", "gp",
                    "kwazulu natal", "kzn", "limpopo", "lp", "mpumalanga", "mp",
                    "northern cape", "nc", "north west", "nw", "cape town", "ct",
                    "cpt", "stellenbosch", "durban", "johannesburg", "joburg",
                    "pretoria", "tshwane", "soweto", "sandton", "midrand",
                    "centurion", "randburg", "port elizabeth", "gqeberha",
                    "east london", "mthatha", "bloemfontein", "kimberley",
                    "polokwane", "nelspruit", "mbombela", "rustenburg",
                    "potchefstroom", "newcastle", "pietermaritzburg",
                    "richards bay", "george", "mossel bay", "knysna", "paarl",
                    "worcester",
                ),
            }[location_scope]
            matches = []
            for term in terms:
                matches.append(f"{normalized_location} ~ %s")
                parameters.append(r"(^| )" + term + r"( |$)")
            conditions.append("(" + " OR ".join(matches) + ")")
        elif location_scope != "all":
            raise ValueError("Unsupported vacancy location scope.")

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
            "items": items, "total": total, "limit": limit, "offset": offset,
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
