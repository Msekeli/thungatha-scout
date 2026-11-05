from uuid import uuid4

from vacancy_api_test_service import vacancy_client


def test_lists_vacancies_for_an_employer() -> None:
    employer_id = uuid4()
    with vacancy_client() as client:
        response = client.get(f"/api/v1/employers/{employer_id}/vacancies")
    assert response.status_code == 200
    assert response.json() == [
        {"employer_id": str(employer_id), "title": "Software Engineer"}
    ]


def test_gets_full_vacancy_detail() -> None:
    vacancy_id = uuid4()
    with vacancy_client() as client:
        response = client.get(f"/api/v1/vacancies/{vacancy_id}")
    assert response.status_code == 200
    assert response.json()["description"] == "<p>Build software.</p>"
    assert response.json()["review_status"] == "needs_verification"


def test_lists_archived_vacancies() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/vacancies/archived")
    assert response.status_code == 200
    assert response.json()[0]["title"] == "Archived vacancy"
