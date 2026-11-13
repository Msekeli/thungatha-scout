import json
from pathlib import Path
from uuid import uuid4

from employer_api_test_doubles import FakeEmployerService


REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "registry" / "employer-source-registry.json"
)

EXPECTED_13 = [
    "Absa",
    "FirstRand",
    "Astron Energy",
    "Tiger Brands",
    "Mondelēz International",
    "PwC",
    "AIG",
    "Hogan Lovells",
    "Levi Strauss & Co.",
    "MRI Software",
    "Damen",
    "Capita",
    "Solenis",
]


def build_service_from_registry():
    service = FakeEmployerService()
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    for item in data["employers"]:
        supported_sources = [
            source
            for source in item.get("sources", [])
            if source.get("ats")
            in {"greenhouse", "lever", "teamtailor", "workday", "workable"}
        ]
        if not supported_sources:
            continue
        emp_id = str(uuid4())
        service.employers.append(
            {
                "id": emp_id,
                "name": item["name"],
                "website_url": item.get("website_url") or item.get("careers_url"),
                "organization_type": item.get(
                    "organization_classification", "unresolved"
                ),
            }
        )
        for s in supported_sources:
            if s["ats"] == "workday":
                service.sources.append(
                    {
                        "id": str(uuid4()),
                        "employer_id": emp_id,
                        "adapter_key": "workday",
                        "source_url": s["official_source_url"],
                        "adapter_config": s["config"],
                    }
                )
    return service