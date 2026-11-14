from uuid import uuid4

from scout.application.employer_contracts import EmployerBrandingUpdate
from scout.persistence.employer_repository import EmployerRepository


class Cursor:
    def fetchone(self):
        return {"id": "saved"}


class ConnectionDouble:
    def __init__(self):
        self.query = None
        self.params = None

    def execute(self, query, params):
        self.query, self.params = query, params
        return Cursor()


def test_branding_discovery_updates_only_the_logo_url_it_validated() -> None:
    connection = ConnectionDouble()
    employer_id = uuid4()
    old_url = "https://cdn.example.com/old-logo.png"
    repository = EmployerRepository(connection)
    repository.update_branding_if_unusable(
        employer_id,
        old_url,
        "https://cdn.example.com/new.png",
        "https://example.com/",
        "official_logo",
    )
    assert "logo_url IS NOT DISTINCT FROM %s" in connection.query
    assert connection.params[-1] == old_url


def test_branding_update_accepts_official_ats_logo_provenance() -> None:
    payload = EmployerBrandingUpdate(
        logo_url="https://careers.example.com/assets/logo",
        logo_source_url="https://careers.example.com/",
        logo_type="official_ats_logo",
    )
    assert payload.logo_type == "official_ats_logo"
