from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.employers import (
    get_employer_service,
    get_employer_source_update_service,
)
from scout.main import app


class FakeEmployerService:
    def __init__(self) -> None:
        self.employers = []

    def list_employers(self, limit: int, offset: int):
        return self.employers[offset : offset + limit]

    def create_employer(self, payload):
        employer = {
            "id": str(uuid4()),
            "name": payload.name,
            "status": "discovered",
            "organization_type": payload.organization_type,
        }
        self.employers.append(employer)
        return employer

    def get_employer(self, employer_id):
        return next(
            (
                employer
                for employer in self.employers
                if employer["id"] == str(employer_id)
            ),
            None,
        )

    def update_branding(self, employer_id, payload):
        employer = self.get_employer(employer_id)
        if employer is None:
            return None
        employer["logo_url"] = str(payload.logo_url) if payload.logo_url else None
        employer["logo_source_url"] = (
            str(payload.logo_source_url) if payload.logo_source_url else None
        )
        return employer

    def create_source(self, payload):
        return {
            "id": str(uuid4()),
            "employer_id": str(payload.employer_id),
            "adapter_key": payload.adapter_key,
            "status": "discovered",
            "permission_status": "unknown",
        }

    def list_sources(self, employer_id):
        return []


def test_employer_registry_api_creates_and_lists_employers() -> None:
    service = FakeEmployerService()
    app.dependency_overrides[get_employer_service] = lambda: service
    client = TestClient(app)

    try:
        created = client.post(
            "/api/v1/employers",
            json={
                "name": "Example Employer",
                "website_url": "https://example.com",
                "city": "Cape Town",
                "province": "Western Cape",
                "country": "South Africa",
            },
        )

        assert created.status_code == 201
        assert created.json()["name"] == "Example Employer"
        assert created.json()["status"] == "discovered"

        listed = client.get("/api/v1/employers")

        assert listed.status_code == 200
        assert len(listed.json()) == 1
        assert listed.json()[0]["id"] == created.json()["id"]
    finally:
        app.dependency_overrides.clear()


def test_employer_registry_api_validates_payloads() -> None:
    client = TestClient(app)

    response = client.post(
        "/api/v1/employers",
        json={"name": "   "},
    )

    assert response.status_code == 422
    assert response.headers["content-type"].startswith("application/problem+json")


def test_employer_source_api_rejects_mismatched_employer_ids() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append(
        {
            "id": str(employer_id),
            "name": "Example Employer",
            "status": "discovered",
        }
    )
    app.dependency_overrides[get_employer_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(uuid4()),
                "adapter_key": "greenhouse",
                "source_url": "https://boards.greenhouse.io/example",
                "normalized_url": "https://boards.greenhouse.io/example",
                "adapter_config": {"slug": "example"},
            },
        )

        assert response.status_code == 422
    finally:
        app.dependency_overrides.clear()


def test_employer_source_api_registers_discovered_source() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append(
        {
            "id": str(employer_id),
            "name": "Example Employer",
            "status": "discovered",
        }
    )
    app.dependency_overrides[get_employer_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.post(
            f"/api/v1/employers/{employer_id}/sources",
            json={
                "employer_id": str(employer_id),
                "adapter_key": "greenhouse",
                "source_url": "https://boards.greenhouse.io/example",
                "normalized_url": "https://boards.greenhouse.io/example",
                "adapter_config": {"slug": "example"},
            },
        )

        assert response.status_code == 201
        assert response.json()["status"] == "discovered"
        assert response.json()["permission_status"] == "unknown"
    finally:
        app.dependency_overrides.clear()


class FakeEmployerSourceUpdateService:
    def __init__(self) -> None:
        self.updated = None

    def update_configuration(self, employer_id, source_id, payload):
        self.updated = (employer_id, source_id, payload)
        return {
            "id": str(source_id),
            "employer_id": str(employer_id),
            "adapter_key": payload.adapter_key,
            "source_url": str(payload.source_url),
            "normalized_url": str(payload.normalized_url),
            "adapter_config": payload.adapter_config,
            "status": "discovered",
            "permission_status": "unknown",
        }


def test_employer_source_api_updates_source_configuration() -> None:
    service = FakeEmployerSourceUpdateService()
    employer_id = uuid4()
    source_id = uuid4()
    app.dependency_overrides[get_employer_source_update_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.put(
            f"/api/v1/employers/{employer_id}/sources/{source_id}",
            json={
                "adapter_key": "greenhouse",
                "source_url": "https://job-boards.greenhouse.io/impact",
                "normalized_url": "https://job-boards.greenhouse.io/impact",
                "adapter_config": {"slug": "impact"},
            },
        )

        assert response.status_code == 200
        assert response.json()["source_url"] == (
            "https://job-boards.greenhouse.io/impact"
        )
        assert response.json()["adapter_config"] == {"slug": "impact"}
        assert service.updated[0] == employer_id
        assert service.updated[1] == source_id
    finally:
        app.dependency_overrides.clear()


def test_employer_source_api_rejects_invalid_updated_adapter_config() -> None:
    service = FakeEmployerSourceUpdateService()
    app.dependency_overrides[get_employer_source_update_service] = lambda: service
    client = TestClient(app)

    try:
        response = client.put(
            f"/api/v1/employers/{uuid4()}/sources/{uuid4()}",
            json={
                "adapter_key": "greenhouse",
                "source_url": "https://job-boards.greenhouse.io/impact",
                "normalized_url": "https://job-boards.greenhouse.io/impact",
                "adapter_config": {"slug": ""},
            },
        )

        assert response.status_code == 422
        assert service.updated is None
    finally:
        app.dependency_overrides.clear()


def test_employer_branding_api_updates_logo_metadata() -> None:
    service = FakeEmployerService()
    employer_id = uuid4()
    service.employers.append(
        {
            "id": str(employer_id),
            "name": "Example Employer",
            "status": "discovered",
        }
    )
    app.dependency_overrides[get_employer_service] = lambda: service
    client = TestClient(app)

    try:
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
    finally:
        app.dependency_overrides.clear()
