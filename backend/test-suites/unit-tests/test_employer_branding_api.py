from uuid import uuid4

from employer_api_test_doubles import FakeEmployerService, client_for

import scout.api.employer_branding_routes as routes
from scout.api.employers import get_employer_service


def test_valid_unverified_logo_is_preserved(monkeypatch) -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    logo_url = "https://cdn.example.com/legacy-logo.png"
    employer = {
        "id": str(employer_id),
        "name": "Example",
        "website_url": "https://example.com",
        "logo_url": logo_url,
        "logo_type": "unverified",
    }
    service.employers.append(employer)
    discovered = []

    async def valid(url):
        return "valid"

    async def discover(*args):
        discovered.append(args)

    monkeypatch.setattr(routes, "inspect_existing_logo", valid)
    monkeypatch.setattr(routes, "discover_employer_logo", discover)
    with client_for(get_employer_service, service) as client:
        response = client.post(f"/api/v1/employers/{employer_id}/branding/discover")
    assert response.status_code == 200
    assert response.json()["logo_url"] == logo_url
    assert discovered == []


def test_discovery_failure_does_not_clear_broken_legacy_url(monkeypatch) -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    old_url = "https://cdn.example.com/missing.png"
    service.employers.append(
        {
            "id": str(employer_id),
            "name": "Example",
            "website_url": "https://example.com",
            "logo_url": old_url,
            "logo_type": "unverified",
        }
    )

    async def invalid(url):
        return "invalid"

    async def no_candidate(*args, **kwargs):
        return None

    monkeypatch.setattr(routes, "inspect_existing_logo", invalid)
    monkeypatch.setattr(routes, "discover_employer_logo", no_candidate)
    with client_for(get_employer_service, service) as client:
        response = client.post(f"/api/v1/employers/{employer_id}/branding/discover")
    assert response.status_code == 200
    assert response.json()["logo_url"] == old_url
    assert service.branding_discovery_updates == 0
