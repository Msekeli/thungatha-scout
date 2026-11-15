class VacancyMetricsTestService:
    def get_dashboard_metrics(self):
        return {
            "total_active": 201,
            "companies_total": 24,
            "new_last_24_hours": 12,
            "old_vacancies": 45,
            "undated_vacancies": 8,
        }
