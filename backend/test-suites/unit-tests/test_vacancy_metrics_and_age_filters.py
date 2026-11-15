from vacancy_api_test_client import vacancy_client


def test_filters_vacancies_by_age_category() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies?age_filter=undated")
    assert response.status_code == 200
    assert response.json()["total"] == 201


def test_rejects_unknown_vacancy_age_filter() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies?age_filter=verified")
    assert response.status_code == 422


def test_returns_database_vacancy_metrics() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/metrics")
    assert response.status_code == 200
    metrics = response.json()
    assert metrics["fresh_vacancies"] == 148
    assert (
        metrics["recent_vacancies"]
        + metrics["aging_vacancies"]
        + metrics["stale_vacancies"]
        == 45
    )
    classified_total = sum(
        metrics[key]
        for key in (
            "fresh_vacancies",
            "recent_vacancies",
            "aging_vacancies",
            "stale_vacancies",
            "undated_vacancies",
        )
    )
    assert classified_total == metrics["total_active"]
    assert metrics["undated_vacancies"] == 8
    assert response.json()["companies_total"] == 24
