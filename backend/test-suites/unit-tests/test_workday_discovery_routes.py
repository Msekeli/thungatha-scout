from fastapi.testclient import TestClient

from scout.api import workday_routes
from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.main import app


def test_workday_discovery_returns_shared_source_contract(monkeypatch) -> None:
    async def retrieve(_adapter, _config):
        return ATSAdapterResult("success", [], 1, True, total_vacancies=3)

    monkeypatch.setattr(workday_routes, "retrieve_adapter_result", retrieve)
    response = TestClient(app).get(
        "/api/v1/workday/discover",
        params={
            "url": "https://myhcm.wd3.myworkdayjobs.com/en-US/digioutsource",
            "company_name": "DigiOutsource",
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["detected_adapter"] == "workday"
    assert payload["adapter_config"] == {
        "host_prefix": "myhcm.wd3", "tenant": "myhcm", "site": "digioutsource"
    }
    assert payload["complete"] is True
    assert payload["total_vacancies"] == 3


def test_workday_discovery_rejects_job_detail_urls() -> None:
    response = TestClient(app).get(
        "/api/v1/workday/discover",
        params={"url": "https://myhcm.wd3.myworkdayjobs.com/job/Cape-Town/Role"},
    )
    assert response.status_code == 422
