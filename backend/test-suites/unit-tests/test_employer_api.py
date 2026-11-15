from uuid import uuid4

from employer_api_test_doubles import FakeEmployerService, client_for

from scout.api.employers import get_employer_service


def test_employer_registry_api_creates_and_lists_employers() -> None:
    service = FakeEmployerService()
    with client_for(get_employer_service, service) as client:
        created = client.post(
            "/api/v1/employers",
            json={
                "name": "Example Employer",
                "website_url": "https://example.com",
                "logo_url": "https://example.com/brand/logo.svg",
                "logo_source_url": "https://example.com/careers",
                "city": "Cape Town",
                "province": "Western Cape",
                "country": "South Africa",
            },
        )
        listed = client.get("/api/v1/employers")
    assert created.status_code == 201
    assert created.json()["name"] == "Example Employer"
    assert "status" not in created.json()
    assert created.json()["logo_url"] == "https://example.com/brand/logo.svg"
    assert created.json()["logo_source_url"] == "https://example.com/careers"
    assert listed.status_code == 200
    assert listed.json()[0]["id"] == created.json()["id"]


def test_employer_registry_api_validates_payloads() -> None:
    from fastapi.testclient import TestClient

    from scout.main import app

    response = TestClient(app).post("/api/v1/employers", json={"name": "   "})
    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


def test_employer_branding_api_updates_logo_metadata() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append({"id": str(employer_id), "name": "Example"})
    with client_for(get_employer_service, service) as client:
        response = client.patch(
            f"/api/v1/employers/{employer_id}/branding",
            json={
                "logo_url": "https://example.com/logo.png",
                "logo_source_url": "https://example.com/about",
            },
        )
    assert response.status_code == 200
    assert response.json()["logo_url"] == "https://example.com/logo.png"
    assert response.json()["logo_source_url"] == "https://example.com/about"


def test_logo_discovery_uses_registered_employer_careers_url(monkeypatch) -> None:

    import scout.api.employer_branding_routes as employer_routes

    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append(
        {
            "id": str(employer_id),
            "name": "Example",
            "website_url": None,
            "logo_type": "unverified",
            "logo_url": None,
        }
    )
    service.sources.append(
        {
            "id": str(uuid4()),
            "employer_id": str(employer_id),
            "employer_careers_url": "https://careers.example.com/jobs",
        }
    )
    discovered = []

    async def fake_discover(careers_url, website_url=None, **kwargs):
        discovered.append((careers_url, website_url))

    monkeypatch.setattr(employer_routes, "discover_employer_logo", fake_discover)
    with client_for(get_employer_service, service) as client:
        response = client.post(f"/api/v1/employers/{employer_id}/branding/discover")

    assert response.status_code == 200
    assert discovered == [("https://careers.example.com/jobs", None)]
