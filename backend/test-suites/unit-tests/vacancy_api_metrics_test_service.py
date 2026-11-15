class VacancyMetricsTestService:
    def get_dashboard_metrics(self):
        return {
            "total_active": 201,
            "companies_total": 24,
            "new_last_24_hours": 12,
            "fresh_vacancies": 148,
            "recent_vacancies": 20,
            "aging_vacancies": 15,
            "stale_vacancies": 10,
            "undated_vacancies": 8,
        }
