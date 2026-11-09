from uuid import uuid4

from vacancy_api_test_client import vacancy_client


def test_lists_vacancies_for_an_employer() -> None:
    employer_id = uuid4()
    with vacancy_client() as client:
        response = client.get(f"/api/v1/employers/{employer_id}/vacancies")
    assert response.status_code == 200
    assert response.json() == [
        {"employer_id": str(employer_id), "title": "Software Engineer"}
    ]


def test_lists_vacancies_with_total_and_pagination_metadata() -> None:
    with vacancy_client() as client:
        response = client.get(
            "/api/v1/vacancies?limit=50&offset=0&location_scope=cape_town"
        )
    assert response.status_code == 200
    assert response.json()["total"] == 201
    assert response.json()["limit"] == 50
    assert response.json()["has_more"] is True
    assert len(response.json()["items"]) == 1


def test_gets_full_vacancy_detail() -> None:
    vacancy_id = uuid4()
    with vacancy_client() as client:
        response = client.get(f"/api/v1/vacancies/{vacancy_id}")
    assert response.status_code == 200
    assert response.json()["description"] == "<p>Build software.</p>"
    assert "review_status" not in response.json()


def test_lists_archived_vacancies() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/archived")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Archived vacancy"


def test_lists_vacancies_for_western_cape_scope() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies?location_scope=western_cape")
    assert response.status_code == 200
    assert response.json()["total"] == 201


def test_rejects_unknown_location_scope() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies?location_scope=sweden")
    assert response.status_code == 422


def test_exports_active_vacancies_with_full_descriptions() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/export?limit=25&offset=50")
    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 81
    assert payload["limit"] == 25
    assert payload["offset"] == 50
    assert payload["has_more"] is True
    assert payload["location_scope"] == "south_africa"
    assert payload["items"][0]["description"] == "Build software."
    assert "external_job_id" not in payload["items"][0]
    assert "source_url" not in payload["items"][0]


def test_exports_vacancies_using_selected_location_scope() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/export?location_scope=cape_town")
    assert response.status_code == 200
    assert response.json()["location_scope"] == "cape_town"


def test_rejects_unknown_export_location_scope() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/export?location_scope=sweden")
    assert response.status_code == 422

