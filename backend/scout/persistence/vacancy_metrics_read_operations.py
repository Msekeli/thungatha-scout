class VacancyMetricsReadOperations:
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
