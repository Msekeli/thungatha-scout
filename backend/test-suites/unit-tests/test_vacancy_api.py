from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancies import get_extraction_service
from scout.main import app


class FakeExtractionService:
    async def extract_source(self, source_id):
        return {
            "id": str(uuid4()),
            "source_id": str(source_id),
            "outcome": "success",
            "jobs_received": 2,
            "jobs_inserted": 2,
            "jobs_updated": 0,
            "complete": True,
        }

    def list_vacancies(self, employer_id=None, limit=200, offset=0):
        return [{"employer_id": str(employer_id), "title": "Software Engineer"}]

    def get_vacancy(self, vacancy_id):
        return {
            "id": str(vacancy_id),
            "title": "Software Engineer",
            "description": "<p>Build software.</p>",
            "review_status": "needs_verification",
        }

    def update_vacancy_review(self, vacancy_id, review_status, review_reason):
        return {
            "id": str(vacancy_id),
            "review_status": review_status,
            "review_reason": review_reason,
        }

    def archive_vacancy(self, vacancy_id, reason):
        return {"id": str(vacancy_id), "archived_reason": reason}

    def restore_vacancy(self, vacancy_id):
        return {"id": str(vacancy_id), "archived_at": None}

    def list_archived_vacancies(self, limit=200, offset=0):
        return [{"id": str(uuid4()), "title": "Archived vacancy"}]

    def list_extraction_runs(self, source_id):
        return [{
            "id": str(uuid4()),
            "source_id": str(source_id),
            "outcome": "not_found",
            "jobs_received": 0,
            "jobs_inserted": 0,
            "jobs_updated": 0,
            "complete": False,
            "detail": "Greenhouse returned HTTP 404.",
        }]


def test_lists_vacancies_for_an_employer() -> None:
    employer_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).get(
            f"/api/v1/employers/{employer_id}/vacancies"
        )
        assert response.status_code == 200
        assert response.json() == [{
            "employer_id": str(employer_id),
            "title": "Software Engineer",
        }]
    finally:
        app.dependency_overrides.clear()


def test_extracts_a_registered_source() -> None:
    source_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).post(
            f"/api/v1/sources/{source_id}/extract"
        )
        assert response.status_code == 200
        assert response.json()["outcome"] == "success"
        assert response.json()["jobs_inserted"] == 2
    finally:
        app.dependency_overrides.clear()


def test_lists_extraction_runs_for_a_source() -> None:
    source_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).get(
            f"/api/v1/sources/{source_id}/extraction-runs"
        )
        assert response.status_code == 200
        assert response.json()[0]["outcome"] == "not_found"
        assert response.json()[0]["detail"] == "Greenhouse returned HTTP 404."
    finally:
        app.dependency_overrides.clear()



def test_gets_vacancy_detail() -> None:
    vacancy_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).get(f"/api/v1/vacancies/{vacancy_id}")
        assert response.status_code == 200
        assert response.json()["description"] == "<p>Build software.</p>"
        assert response.json()["review_status"] == "needs_verification"
    finally:
        app.dependency_overrides.clear()


def test_updates_vacancy_review_status() -> None:
    vacancy_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).patch(
            f"/api/v1/vacancies/{vacancy_id}/review",
            json={"review_status": "verified", "review_reason": "Cape Town office confirmed."},
        )
        assert response.status_code == 200
        assert response.json()["review_status"] == "verified"
    finally:
        app.dependency_overrides.clear()


def test_archives_and_restores_vacancy() -> None:
    vacancy_id = uuid4()
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        client = TestClient(app)
        archived = client.post(
            f"/api/v1/vacancies/{vacancy_id}/archive",
            json={"reason": "Duplicate listing"},
        )
        restored = client.post(f"/api/v1/vacancies/{vacancy_id}/restore")
        assert archived.status_code == 200
        assert archived.json()["archived_reason"] == "Duplicate listing"
        assert restored.status_code == 200
        assert restored.json()["archived_at"] is None
    finally:
        app.dependency_overrides.clear()


def test_lists_archived_vacancies_static_route() -> None:
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).get("/api/v1/vacancies/archived")
        assert response.status_code == 200
        assert response.json()[0]["title"] == "Archived vacancy"
    finally:
        app.dependency_overrides.clear()
