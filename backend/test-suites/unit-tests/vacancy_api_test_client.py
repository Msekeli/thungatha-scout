from contextlib import contextmanager

from fastapi.testclient import TestClient
from vacancy_api_test_service import FakeExtractionService

from scout.api.vacancies import get_extraction_service
from scout.main import app


@contextmanager
def vacancy_client():
    app.dependency_overrides[get_extraction_service] = FakeExtractionService
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
