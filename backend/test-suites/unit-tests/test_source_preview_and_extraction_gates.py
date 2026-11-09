from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancy_api_dependencies import get_source_preview_service
from scout.api.vacancies import get_extraction_service
from scout.application.source_extraction_errors import SourceNotApprovedError
from scout.main import app
from source_preview_api_test_service import FakeSourcePreviewService
from vacancy_api_test_service import FakeExtractionService


def test_extract_rejects_unapproved_source() -> None:
    class UnapprovedExtractionService(FakeExtractionService):
        async def extract_source(self, source_id):
            raise SourceNotApprovedError(
                "Source extraction requires verified status and allowed permission."
            )

    app.dependency_overrides[get_extraction_service] = UnapprovedExtractionService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/extract")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 409


def test_previews_registered_source_without_persisting_vacancies() -> None:
    app.dependency_overrides[get_source_preview_service] = FakeSourcePreviewService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/preview")
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert response.json()["discovery_preview"]["total_vacancies"] == 7
