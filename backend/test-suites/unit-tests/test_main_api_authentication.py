from fastapi.testclient import TestClient

from scout.authentication import require_admin
from scout.main import app


def test_admin_api_routes_reject_requests_without_a_session():
    app.dependency_overrides.pop(require_admin, None)
    try:
        response = TestClient(app).get("/api/v1/employers")
    finally:
        app.dependency_overrides[require_admin] = lambda: {
            "sub": "test-administrator",
            "email": "admin@example.com",
        }

    assert response.status_code == 401


def test_health_endpoint_remains_public():
    response = TestClient(app).get("/health")

    assert response.status_code == 200
