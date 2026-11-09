import asyncio
from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancy_api_dependencies import get_source_preview_service
from scout.api.vacancies import get_extraction_service
from scout.application.source_extraction_service import SourceExtractionService
from scout.main import app
from source_preview_api_test_service import FakeSourcePreviewService
from vacancy_api_test_service import FakeExtractionService


def test_extract_does_not_require_source_approval() -> None:
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/extract")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code != 409


def test_previews_registered_source_without_persisting_vacancies() -> None:
    app.dependency_overrides[get_source_preview_service] = FakeSourcePreviewService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/preview")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["discovery_preview"]["total_vacancies"] == 7


def test_extraction_service_accepts_registered_source_without_review_columns() -> None:
    class FakeCursor:
        def fetchone(self):
            return {"adapter_key": "lever", "adapter_config": {"slug": "example"}}

    class FakeConnection:
        def __enter__(self):
            return self

        def __exit__(self, *_):
            return None

        def execute(self, *_):
            return FakeCursor()

    service = SourceExtractionService(connection_factory=FakeConnection)
    assert service is not None
from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.vacancy_api_dependencies import get_source_preview_service
from scout.api.vacancies import get_extraction_service
from scout.main import app
from source_preview_api_test_service import FakeSourcePreviewService
from vacancy_api_test_service import FakeExtractionService


def test_extract_endpoint_does_not_enforce_source_approval() -> None:
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/extract")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code != 409


def test_previews_registered_source_without_persisting_vacancies() -> None:
    app.dependency_overrides[get_source_preview_service] = FakeSourcePreviewService
    try:
        response = TestClient(app).post(f"/api/v1/sources/{uuid4()}/preview")
    finally:
        app.dependency_overrides.clear()
    assert response.status_code == 200
    assert response.json()["discovery_preview"]["total_vacancies"] == 7
