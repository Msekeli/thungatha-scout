from uuid import uuid4

from vacancy_api_test_service import vacancy_client


def test_extracts_a_registered_source() -> None:
    source_id = uuid4()
    with vacancy_client() as client:
        response = client.post(f"/api/v1/sources/{source_id}/extract")
    assert response.status_code == 200
    assert response.json()["outcome"] == "success"
    assert response.json()["jobs_inserted"] == 2


def test_lists_extraction_runs_for_a_source() -> None:
    source_id = uuid4()
    with vacancy_client() as client:
        response = client.get(f"/api/v1/sources/{source_id}/extraction-runs")
    assert response.status_code == 200
    assert response.json()[0]["outcome"] == "not_found"


def test_bulk_extraction_history_returns_all_source_runs() -> None:
    with vacancy_client() as client:
        response = client.get("/api/v1/extraction-runs")
    assert response.status_code == 200
    assert response.json() == [{"source_id": "source-1", "outcome": "success"}]



def test_removed_review_endpoint_is_not_available() -> None:
    vacancy_id = uuid4()
    with vacancy_client() as client:
        response = client.patch(
            f"/api/v1/vacancies/{vacancy_id}/review",
            json={"review_status": "verified"},
        )
    assert response.status_code == 404


def test_archives_and_restores_vacancy() -> None:
    vacancy_id = uuid4()
    with vacancy_client() as client:
        archived = client.post(
            f"/api/v1/vacancies/{vacancy_id}/archive",
            json={"reason": "Duplicate listing"},
        )
        restored = client.post(f"/api/v1/vacancies/{vacancy_id}/restore")
    assert archived.status_code == 200
    assert archived.json()["archived_reason"] == "Duplicate listing"
    assert restored.status_code == 200
    assert restored.json()["archived_at"] is None
