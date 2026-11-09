from contextlib import contextmanager
from uuid import uuid4

from fastapi.testclient import TestClient

from scout.main import app


class FakeEmployerService:
    def __init__(self) -> None:
        self.employers = []
        self.sources = []

    def list_employers(self, limit: int, offset: int):
        return self.employers[offset : offset + limit]

    def create_employer(self, payload):
        row = {
            "id": str(uuid4()),
            "name": payload.name,
            "organization_type": payload.organization_type,
            "logo_url": str(payload.logo_url) if payload.logo_url else None,
            "logo_source_url": str(payload.logo_source_url)
            if payload.logo_source_url
            else None,
        }
        self.employers.append(row)
        return row

    def get_employer(self, employer_id):
        return next(
            (row for row in self.employers if row["id"] == str(employer_id)), None
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
        row = {
            "id": str(uuid4()),
            "employer_id": str(payload.employer_id),
            "adapter_key": payload.adapter_key,
            "discovery_preview": (
                payload.discovery_preview.model_dump(mode="json")
                if payload.discovery_preview
                else None
            ),
        }
        self.sources.append(row)
        return row

    def list_sources(self, employer_id):
        return [row for row in self.sources if row["employer_id"] == str(employer_id)]

    def list_all_sources(self):
        return self.sources


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
        }


@contextmanager
def client_for(dependency, service):
    app.dependency_overrides[dependency] = lambda: service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
