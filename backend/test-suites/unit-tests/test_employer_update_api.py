from uuid import uuid4

from fastapi.testclient import TestClient

from scout.api.employers import get_employer_service
from scout.main import app


class EmployerUpdateServiceDouble:
    def __init__(self):
        self.updated = None

    def update_details(self, employer_id, payload):
        self.updated = (employer_id, payload)
        return {"id": str(employer_id), "name": payload.name, "website_url": str(payload.website_url) if payload.website_url else None, "organization_type": payload.organization_type}


def test_employer_update_api_updates_company_identity():
    service = EmployerUpdateServiceDouble()
    employer_id = uuid4()
    app.dependency_overrides[get_employer_service] = lambda: service
    try:
        response = TestClient(app).patch(
            f"/api/v1/employers/{employer_id}",
            json={"name": "Updated Employer", "website_url": "https://updated.example", "organization_type": "direct_employer"},
        )
        assert response.status_code == 200
        assert response.json()["name"] == "Updated Employer"
        assert service.updated[0] == employer_id
    finally:
        app.dependency_overrides.clear()


def test_employer_update_api_rejects_blank_company_name():
    response = TestClient(app).patch(
        f"/api/v1/employers/{uuid4()}",
        json={"name": "   ", "organization_type": "unresolved"},
    )
    assert response.status_code == 422
