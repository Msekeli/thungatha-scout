import json
from pathlib import Path
from uuid import uuid4
from employer_api_test_doubles import FakeEmployerService, client_for
from scout.api.employers import get_employer_service

REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "registry" / "employer-source-registry.json"
)

EXPECTED_13 = [
    "Absa", "FirstRand", "Astron Energy", "Tiger Brands",
    "Mondelēz International", "PwC", "AIG", "Hogan Lovells",
    "Levi Strauss & Co.", "MRI Software", "Damen", "Capita", "Solenis",
]


def _build_service_from_registry():
    service = FakeEmployerService()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for item in data["employers"]:
        supported_sources = [
            source
            for source in item.get("sources", [])
            if source.get("ats") in {"greenhouse", "lever", "teamtailor", "workday", "workable"}
        ]
        if not supported_sources:
            continue
        emp_id = str(uuid4())
        service.employers.append({
            "id": emp_id,
            "name": item["name"],
            "website_url": item.get("website_url") or item.get("careers_url"),
            "organization_type": item.get("organization_classification", "unresolved"),
        })
        for s in supported_sources:
            if s["ats"] == "workday":
                service.sources.append({
                    "id": str(uuid4()),
                    "employer_id": emp_id,
                    "adapter_key": "workday",
                    "source_url": s["official_source_url"],
                    "adapter_config": s["config"],
                })
    return service


def test_workday_employers_are_visible_through_api() -> None:
    service = _build_service_from_registry()
    with client_for(get_employer_service, service) as client:
        resp = client.get("/api/v1/employers?limit=100")
        assert resp.status_code == 200
        data = resp.json()
        names = {item["name"] for item in data}
        for name in EXPECTED_13:
            assert name in names, f"{name} is not visible in employers API."

        sources_resp = client.get("/api/v1/employers/sources")
        assert sources_resp.status_code == 200
        sources_data = sources_resp.json()
        assert len(sources_data) == 16
        for s in sources_data:
            assert s["adapter_key"] == "workday"
            assert "host_prefix" in s["adapter_config"]
            assert "tenant" in s["adapter_config"]
            assert "site" in s["adapter_config"]

        absa = next(item for item in data if item["name"] == "Absa")
        absa_sources_resp = client.get(f"/api/v1/employers/{absa['id']}/sources")
        assert absa_sources_resp.status_code == 200
        absa_sources = absa_sources_resp.json()
        assert len(absa_sources) == 1
        assert absa_sources[0]["adapter_config"]["tenant"] == "absa"


def test_existing_workday_employers_remain_visible_without_duplicates() -> None:
    service = _build_service_from_registry()
    with client_for(get_employer_service, service) as client:
        employers = client.get("/api/v1/employers?limit=100").json()
        sources = client.get("/api/v1/employers/sources").json()

    assert len(employers) == 23
    assert len(sources) == 16
    assert sum(item["name"] == "DigiOutsource" for item in employers) == 1
    assert sum(item["name"] == "Old Mutual" for item in employers) == 1
    assert sum(item["name"] == "Pick n Pay" for item in employers) == 1
    assert sum(source["adapter_key"] == "workday" for source in sources) == 16
