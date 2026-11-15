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
    assert response.json()["old_vacancies"] == 45
    assert response.json()["undated_vacancies"] == 8
    assert response.json()["companies_total"] == 24
