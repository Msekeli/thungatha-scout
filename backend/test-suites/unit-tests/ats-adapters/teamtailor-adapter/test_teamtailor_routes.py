from fastapi.testclient import TestClient

from scout.api import teamtailor_routes
from scout.ats_adapters.ats_adapter_contracts import (
    ATSAdapterResult,
    NormalizedVacancy,
)
from scout.main import app


class FakeTeamtailorAdapter:
    channel_title = "Root Platform"

    async def retrieve(self, config):
        vacancy = NormalizedVacancy(
            "job-1",
            "Engineer",
            "Build software",
            "Cape Town",
            "Engineering",
            None,
            "https://root.teamtailor.com/jobs/job-1",
            None,
            None,
            {"link": "https://root.teamtailor.com/jobs/job-1"},
        )
        return ATSAdapterResult("success", [vacancy], 1, True, None, 1)

    async def close(self):
        return None


def test_teamtailor_discovery_returns_adapter_config(monkeypatch) -> None:
    monkeypatch.setattr(
        teamtailor_routes, "TeamtailorSourceAdapter", FakeTeamtailorAdapter
    )
    response = TestClient(app).get(
        "/api/v1/teamtailor/discover",
        params={"url": "https://root.teamtailor.com/jobs"},
    )
    assert response.status_code == 200
    assert response.json()["detected_adapter"] == "teamtailor"
    assert response.json()["adapter_config"] == {
        "careers_url": "https://root.teamtailor.com/jobs"
    }
    assert response.json()["jobs"][0]["absolute_url"].endswith("job-1")


class MissingTeamtailorAdapter(FakeTeamtailorAdapter):
    channel_title = None

    async def retrieve(self, config):
        return ATSAdapterResult("not_found", [], 0, False, "Feed not found.", None)


def test_non_teamtailor_jobs_url_can_fall_back_to_other_discovery(monkeypatch) -> None:
    monkeypatch.setattr(
        teamtailor_routes, "TeamtailorSourceAdapter", MissingTeamtailorAdapter
    )
    response = TestClient(app).get(
        "/api/v1/teamtailor/discover",
        params={"url": "https://example.com/jobs"},
    )
    assert response.status_code == 404
