from fastapi.testclient import TestClient

from scout.api import workable_routes
from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.main import app


def test_workable_discovery_returns_shared_source_contract(monkeypatch) -> None:
    async def retrieve(_adapter, _config):
        return ATSAdapterResult(
            "success",
            [],
            1,
            True,
            None,
            total_vacancies=None,
        )

    monkeypatch.setattr(workable_routes, "retrieve_adapter_result", retrieve)
    response = TestClient(app).get(
        "/api/v1/workable/discover",
        params={"url": "https://apply.workable.com/electrum/", "company_name": "Electrum"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_adapter"] == "workable"
    assert payload["adapter_config"] == {"slug": "electrum"}
    assert payload["board_url"] == "https://apply.workable.com/electrum"
    assert payload["complete"] is True


def test_workable_discovery_rejects_job_detail_urls() -> None:
    response = TestClient(app).get(
        "/api/v1/workable/discover",
        params={"url": "https://apply.workable.com/electrum/jobs/123"},
    )

    assert response.status_code == 422
