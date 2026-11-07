from datetime import datetime, timezone
from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancies import get_extraction_service
from scout.main import app
from scout.settings import Settings, get_settings
from vacancy_api_test_service import FakeExtractionService


def test_export_returns_the_documented_scout_contract() -> None:
    vacancy_id = uuid4()

    class ExportService(FakeExtractionService):
        def export_vacancies(self, limit=50, offset=0, location_scope="south_africa"):
            return {
                "items": [
                    {
                        "scout_vacancy_id": vacancy_id,
                        "employer_name": "Example Employer",
                        "logo_url": None,
                        "title": "Software Engineer",
                        "description": "<p>Build software.</p>",
                        "location_text": "Cape Town, South Africa",
                        "application_url": "https://jobs.example.com/apply/123",
                        "published_at": datetime(2026, 11, 1, tzinfo=timezone.utc),
                        "source_updated_at": None,
                        "first_seen_at": datetime(2026, 11, 2, tzinfo=timezone.utc),
                    }
                ],
                "total": 1,
                "limit": limit,
                "offset": offset,
                "has_more": False,
                "location_scope": location_scope,
            }

    app.dependency_overrides[get_extraction_service] = ExportService
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/vacancies/export")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    payload = response.json()
    assert payload["location_scope"] == "south_africa"
    assert payload["items"][0] == {
        "scout_vacancy_id": str(vacancy_id),
        "employer_name": "Example Employer",
        "logo_url": None,
        "title": "Software Engineer",
        "description": "<p>Build software.</p>",
        "location_text": "Cape Town, South Africa",
        "application_url": "https://jobs.example.com/apply/123",
        "published_at": "2026-11-01T00:00:00Z",
        "source_updated_at": None,
        "first_seen_at": "2026-11-02T00:00:00Z",
    }


def test_export_requires_the_configured_server_to_server_key() -> None:
    settings = Settings(
        app_env="production",
        scout_export_api_key="test-export-key",
    )
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as client:
            missing_key = client.get("/api/v1/vacancies/export")
            valid_key = client.get(
                "/api/v1/vacancies/export",
                headers={"X-Scout-Export-Key": "test-export-key"},
            )
    finally:
        app.dependency_overrides.clear()

    assert missing_key.status_code == 401
    assert valid_key.status_code == 200


def test_export_fails_closed_in_production_without_a_key() -> None:
    settings = Settings(app_env="production")
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    app.dependency_overrides[get_settings] = lambda: settings
    try:
        with TestClient(app) as client:
            response = client.get("/api/v1/vacancies/export")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 503
