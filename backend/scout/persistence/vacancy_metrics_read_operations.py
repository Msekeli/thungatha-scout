class VacancyMetricsReadOperations:
    def get_dashboard_metrics(self) -> dict[str, int]:
        row = self._connection.execute(
            """
            SELECT COUNT(*) AS total_active,
                COUNT(*) FILTER (WHERE first_seen_at >= NOW() - INTERVAL '24 hours')
                    AS new_last_24_hours,
                COUNT(*) FILTER (WHERE COALESCE(source_updated_at, published_at)
                    < NOW() - INTERVAL '8 days') AS old_vacancies,
                COUNT(*) FILTER (WHERE source_updated_at IS NULL
                    AND published_at IS NULL) AS undated_vacancies
            FROM vacancies
            WHERE status = 'active' AND archived_at IS NULL
            """
        ).fetchone()
        keys = (
            "total_active",
            "new_last_24_hours",
            "old_vacancies",
            "undated_vacancies",
        )
        return {key: row[key] for key in keys}
