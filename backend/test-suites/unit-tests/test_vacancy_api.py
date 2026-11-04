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
