from fastapi import HTTPException
from fastapi.testclient import TestClient

from scout.main import app

client = TestClient(app)


def test_health_endpoint_returns_healthy_status() -> None:
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "thungatha-scout-api",
    }


def test_http_errors_use_problem_details_format() -> None:
    @app.get("/test-http-error")
    def raise_http_error() -> None:
        raise HTTPException(status_code=404, detail="Source not found")

    response = client.get("/test-http-error")

    assert response.status_code == 404
    assert response.headers["content-type"].startswith("application/problem+json")
    assert response.json() == {
        "type": "about:blank",
        "title": "Request failed",
        "status": 404,
        "detail": "Source not found",
        "instance": "/test-http-error",
    }


def test_validation_errors_use_problem_details_format() -> None:
    @app.get("/test-validation-error")
    def validation_error(limit: int) -> dict[str, int]:
        return {"limit": limit}

    response = client.get("/test-validation-error?limit=invalid")

    assert response.status_code == 422
    body = response.json()
    assert body["type"] == "about:blank"
    assert body["title"] == "Request validation failed"
    assert body["status"] == 422
    assert body["instance"] == "/test-validation-error"
    assert body["errors"]


