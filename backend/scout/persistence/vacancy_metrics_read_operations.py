class VacancyMetricsReadOperations:
    def get_dashboard_metrics(self) -> dict[str, int]:
        row = self._connection.execute(
            """
            SELECT COUNT(*) AS total_active,
                (SELECT COUNT(*) FROM employers) AS companies_total,
                COUNT(*) FILTER (WHERE first_seen_at >= NOW() - INTERVAL '24 hours')
                    AS new_last_24_hours,
                COUNT(*) FILTER (WHERE COALESCE(source_updated_at, published_at)
                    >= NOW() - INTERVAL '8 days') AS fresh_vacancies,
                COUNT(*) FILTER (WHERE COALESCE(source_updated_at, published_at)
                    < NOW() - INTERVAL '8 days'
                    AND COALESCE(source_updated_at, published_at)
                    >= NOW() - INTERVAL '15 days') AS recent_vacancies,
                COUNT(*) FILTER (WHERE COALESCE(source_updated_at, published_at)
                    < NOW() - INTERVAL '15 days'
                    AND COALESCE(source_updated_at, published_at)
                    >= NOW() - INTERVAL '31 days') AS aging_vacancies,
                COUNT(*) FILTER (WHERE COALESCE(source_updated_at, published_at)
                    < NOW() - INTERVAL '31 days') AS stale_vacancies,
                COUNT(*) FILTER (WHERE source_updated_at IS NULL
                    AND published_at IS NULL) AS undated_vacancies
            FROM vacancies
            WHERE status = 'active' AND archived_at IS NULL
            """
        ).fetchone()
        keys = (
            "total_active",
            "companies_total",
            "new_last_24_hours",
            "fresh_vacancies",
            "recent_vacancies",
            "aging_vacancies",
            "stale_vacancies",
            "undated_vacancies",
        )
        return {key: row[key] for key in keys}
