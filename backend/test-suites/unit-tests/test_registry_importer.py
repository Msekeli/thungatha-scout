from registry_importer_test_connection import FakeConnection
from scout.registry_importer import import_registry


def test_registry_import_is_repeat_safe_for_supported_adapters() -> None:
    registry = {
        "employers": [
            {
                "name": "Greenhouse Employer",
                "careers_url": "https://example.com/careers",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": (
                            "https://job-boards.greenhouse.io/example"
                        ),
                        "config": {"slug": "example"},
                    }
                ],
            },
            {
                "name": "Workday Employer",
                "sources": [
                    {
                        "ats": "workday",
                        "official_source_url": (
                            "https://example.wd3.myworkdayjobs.com/Careers"
                        ),
                        "config": {
                            "host_prefix": "example.wd3",
                            "tenant": "example",
                            "site": "Careers",
                        },
                    }
                ],
            },
            {
                "name": "Mama Money",
                "sources": [
                    {
                        "ats": "lever",
                        "official_source_url": "https://jobs.lever.co/mamamoney",
                        "config": {"slug": "mamamoney", "region": "global"},
                    }
                ],
            },
        ]
    }
    connection = FakeConnection()

    first = import_registry(registry, connection)
    second = import_registry(registry, connection)

    assert first == {
        "employers_created": 3,
        "employers_updated": 0,
        "sources_created": 3,
        "sources_updated": 0,
        "sources_skipped": 0,
    }
    assert second == {
        "employers_created": 0,
        "employers_updated": 0,
        "sources_created": 0,
        "sources_updated": 0,
        "sources_skipped": 0,
    }


def test_registry_import_skips_unsupported_sources() -> None:
    registry = {
        "employers": [
            {
                "name": "Recruitment Agency",
                "sources": [
                    {
                        "ats": "placement_partner",
                        "official_source_url": "https://example.com/jobs",
                        "config": {"agency_id": "example"},
                    }
                ],
            }
        ]
    }

    result = import_registry(registry, FakeConnection())

    assert result["employers_created"] == 1
    assert result["sources_created"] == 0
    assert result["sources_skipped"] == 1
