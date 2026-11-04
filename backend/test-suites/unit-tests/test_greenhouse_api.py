from fastapi.testclient import TestClient

from scout.main import app


def test_greenhouse_inspection_rejects_non_greenhouse_url() -> None:
    response = TestClient(app).get(
        "/api/v1/greenhouse/inspect",
        params={"url": "https://example.com/careers"},
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith(
        "application/problem+json"
    )
