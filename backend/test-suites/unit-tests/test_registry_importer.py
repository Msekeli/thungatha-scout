from uuid import uuid4

import pytest

from scout.registry_importer import import_registry


class FakeResult:
    def __init__(self, row=None):
        self.row = row

    def fetchone(self):
        return self.row

    def fetchall(self):
        return self.row or []


class FakeConnection:
    def __init__(self):
        self.employers = []
        self.sources = []

    def execute(self, query, params=()):
        if "SELECT id, website_url FROM employers" in query:
            row = next(
                (item for item in self.employers if item["name"] == params[0]),
                None,
            )
            return FakeResult(row)
        if "INSERT INTO employers" in query:
            row = {
                "id": uuid4(),
                "name": params[0],
                "website_url": params[1],
            }
            self.employers.append(row)
            return FakeResult(row)
        if "SELECT id, employer_id, adapter_key" in query:
            row = next(
                (item for item in self.sources if item["normalized_url"] == params[0]),
                None,
            )
            return FakeResult(row)
        if "SELECT id, normalized_url" in query:
            rows = [
                item
                for item in self.sources
                if item["employer_id"] == params[0] and item["adapter_key"] == params[1]
            ]
            return FakeResult(rows)
        if "UPDATE employer_sources" in query:
            source_id = params[2] if len(params) == 3 else params[3]
            row = next(item for item in self.sources if item["id"] == source_id)
            row["source_url"] = params[0]
            if len(params) == 4:
                row["normalized_url"] = params[1]
                row["adapter_config"] = params[2].obj
            else:
                row["adapter_config"] = params[1].obj
            return FakeResult(row)
        if "INSERT INTO employer_sources" in query:
            self.sources.append(
                {
                    "id": uuid4(),
                    "employer_id": params[0],
                    "adapter_key": params[1],
                    "source_url": params[2],
                    "normalized_url": params[4],
                    "adapter_config": params[5].obj,
                    "status": "discovered",
                    "permission_status": "unknown",
                }
            )
            return FakeResult()
        raise AssertionError(f"Unexpected SQL: {query}")


def test_registry_import_is_repeat_safe_for_greenhouse_and_workday() -> None:
    registry = {
        "employers": [
            {
                "name": "Example Greenhouse Employer",
                "careers_url": "https://example.com/careers",
                "organization_classification": "direct_employer",
                "cape_town_presence_claimed": True,
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/example",
                        "config": {"slug": "example"},
                        "verification_evidence": ["https://example.com/careers"],
                    }
                ],
            },
            {
                "name": "Example Workday Employer",
                "careers_url": "https://workday.example.com/careers",
                "organization_classification": "direct_employer",
                "sources": [
                    {
                        "ats": "workday",
                        "official_source_url": "https://example.wd3.myworkdayjobs.com/Careers",
                        "config": {
                            "host_prefix": "example.wd3",
                            "tenant": "example",
                            "site": "Careers",
                        },
                        "verification_evidence": [],
                    }
                ],
            },
        ]
    }
    connection = FakeConnection()

    first = import_registry(registry, connection)
    second = import_registry(registry, connection)

    assert first == {
        "employers_created": 2,
        "sources_created": 2,
        "sources_updated": 0,
    }
    assert second == {
        "employers_created": 0,
        "sources_created": 0,
        "sources_updated": 0,
    }
    assert len(connection.employers) == 2
    assert len(connection.sources) == 2


def test_registry_import_rejects_adapters_outside_v1_scope() -> None:
    registry = {
        "employers": [
            {
                "name": "Unsupported",
                "sources": [
                    {
                        "ats": "lever",
                        "official_source_url": "https://jobs.example.com",
                    }
                ],
            }
        ]
    }

    with pytest.raises(ValueError, match="Greenhouse/Workday registry"):
        import_registry(registry, FakeConnection())


def test_registry_import_reconciles_changed_source_url_and_config() -> None:
    connection = FakeConnection()
    employer_id = uuid4()
    connection.employers.append(
        {
            "id": employer_id,
            "name": "Impact.com",
            "website_url": "https://impact.com/careers/",
        }
    )
    connection.sources.append(
        {
            "id": uuid4(),
            "employer_id": employer_id,
            "adapter_key": "greenhouse",
            "source_url": "https://job-boards.greenhouse.io/earlycareersct",
            "normalized_url": "https://job-boards.greenhouse.io/earlycareersct",
            "adapter_config": {"slug": "earlycareersct"},
            "status": "discovered",
            "permission_status": "unknown",
        }
    )
    registry = {
        "employers": [
            {
                "name": "Impact.com",
                "careers_url": "https://impact.com/careers/",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/impact",
                        "config": {"slug": "impact"},
                        "verification_evidence": [],
                    }
                ],
            }
        ]
    }

    result = import_registry(registry, connection)

    assert result == {
        "employers_created": 0,
        "sources_created": 0,
        "sources_updated": 1,
    }
    source = connection.sources[0]
    assert source["source_url"] == "https://job-boards.greenhouse.io/impact"
    assert source["normalized_url"] == "https://job-boards.greenhouse.io/impact"
    assert source["adapter_config"] == {"slug": "impact"}
    assert source["status"] == "discovered"
    assert source["permission_status"] == "unknown"


def test_registry_import_refuses_ambiguous_source_reconciliation() -> None:
    connection = FakeConnection()
    employer_id = uuid4()
    connection.employers.append(
        {
            "id": employer_id,
            "name": "Impact.com",
            "website_url": "https://impact.com/careers/",
        }
    )
    for slug in ("impact-old", "impact-older"):
        connection.sources.append(
            {
                "id": uuid4(),
                "employer_id": employer_id,
                "adapter_key": "greenhouse",
                "source_url": f"https://job-boards.greenhouse.io/{slug}",
                "normalized_url": f"https://job-boards.greenhouse.io/{slug}",
                "adapter_config": {"slug": slug},
                "status": "discovered",
                "permission_status": "unknown",
            }
        )
    registry = {
        "employers": [
            {
                "name": "Impact.com",
                "careers_url": "https://impact.com/careers/",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/impact",
                        "config": {"slug": "impact"},
                        "verification_evidence": [],
                    }
                ],
            }
        ]
    }

    with pytest.raises(ValueError, match="Cannot safely reconcile multiple"):
        import_registry(registry, connection)


def test_registry_import_updates_config_when_source_url_already_matches() -> None:
    connection = FakeConnection()
    employer_id = uuid4()
    connection.employers.append(
        {
            "id": employer_id,
            "name": "Impact.com",
            "website_url": "https://impact.com/careers/",
        }
    )
    connection.sources.append(
        {
            "id": uuid4(),
            "employer_id": employer_id,
            "adapter_key": "greenhouse",
            "source_url": "https://job-boards.greenhouse.io/impact",
            "normalized_url": "https://job-boards.greenhouse.io/impact",
            "adapter_config": {"slug": "earlycareersct"},
            "status": "discovered",
            "permission_status": "unknown",
        }
    )
    registry = {
        "employers": [
            {
                "name": "Impact.com",
                "careers_url": "https://impact.com/careers/",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/impact",
                        "config": {"slug": "impact"},
                        "verification_evidence": [],
                    }
                ],
            }
        ]
    }

    result = import_registry(registry, connection)

    assert result["sources_updated"] == 1
    assert result["sources_created"] == 0
    assert connection.sources[0]["adapter_config"] == {"slug": "impact"}
