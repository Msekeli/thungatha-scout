from fastapi.testclient import TestClient

from scout.api.employers import get_employer_service
from scout.main import app
from employer_api_test_doubles import FakeEmployerService, client_for


def test_employer_registry_api_creates_and_lists_employers() -> None:
    service = FakeEmployerService()
    with client_for(get_employer_service, service) as client:
        created = client.post("/api/v1/employers", json={
            "name": "Example Employer", "website_url": "https://example.com",
            "city": "Cape Town", "province": "Western Cape",
            "country": "South Africa",
        })
        listed = client.get("/api/v1/employers")
    assert created.status_code == 201
    assert created.json()["status"] == "discovered"
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == created.json()["id"]


def test_employer_registry_api_validates_payloads() -> None:
    response = TestClient(app).post("/api/v1/employers", json={"name": "   "})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


def test_employer_registry_api_applies_pagination() -> None:
    service = FakeEmployerService()
    service.employers.extend([{"id": str(i), "name": str(i)} for i in range(3)])
    with client_for(get_employer_service, service) as client:
        response = client.get("/api/v1/employers?limit=1&offset=1")
    assert response.status_code == 200
    assert response.json() == [{"id": "1", "name": "1"}]
