import json
from pathlib import Path
from registry_importer_test_connection import FakeConnection
from scout.registry_importer import import_registry

REGISTRY_PATH = (
    Path(__file__).resolve().parents[2] / "registry" / "employer-source-registry.json"
)
TARGETS_PATH = (
    Path(__file__).resolve().parents[2]
    / "registry"
    / "workday-investigation-targets.json"
)

EXPECTED_MISSING_13 = {
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
}


def test_workday_registry_imports_all_13_missing_employers() -> None:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    targets = json.loads(TARGETS_PATH.read_text(encoding="utf-8"))["targets"]
    conn = FakeConnection()
    counts = import_registry(data, conn)

    assert sum(source["adapter_key"] == "workday" for source in conn.sources) == 16
    emp_by_name = {e["name"]: e for e in conn.employers}
    for name in EXPECTED_MISSING_13:
        assert name in emp_by_name, f"Missing employer: {name}"

    assert "Old Mutual" in emp_by_name
    assert "DigiOutsource" in emp_by_name
    assert "Pick n Pay" in emp_by_name

    pnp_id = emp_by_name["Pick n Pay"]["id"]
    pnp_sources = [s for s in conn.sources if s["employer_id"] == pnp_id]
    assert len(pnp_sources) == 1
    assert pnp_sources[0]["adapter_config"]["site"] == "Pnet"

    workday_sources = [s for s in conn.sources if s["adapter_key"] == "workday"]
    assert len(workday_sources) == len(targets) == 16
    assert len({s["normalized_url"] for s in workday_sources}) == 16
    expected_urls = {
        target["board_url"]
        for target in targets
        if target["employer_id"] != "pick_n_pay"
    }
    expected_urls.add("https://picknpay.wd3.myworkdayjobs.com/Pnet")
    assert {s["normalized_url"] for s in workday_sources} == expected_urls
    assert all(
        len(
            [
                source
                for source in conn.sources
                if source["employer_id"] == employer["id"]
            ]
        )
        == 1
        for employer in conn.employers
    )


def test_workday_registry_import_is_repeat_safe_and_idempotent() -> None:
    data = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
    conn = FakeConnection()
    first_counts = import_registry(data, conn)
    emp_count = len(conn.employers)
    src_count = len(conn.sources)

    second_counts = import_registry(data, conn)
    assert second_counts["employers_created"] == 0
    assert second_counts["employers_updated"] == 0
    assert second_counts["sources_created"] == 0
    assert second_counts["sources_updated"] == 0
    assert len(conn.employers) == emp_count
    assert len(conn.sources) == src_count
