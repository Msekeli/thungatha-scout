import pytest

from scout.registry_importer import import_registry
from registry_importer_test_connection import FakeConnection


def test_registry_import_is_repeat_safe_for_greenhouse_and_workday() -> None:
    registry = {
        "employers": [
            {
                "name": "Greenhouse Employer",
                "careers_url": "https://example.com/careers",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/example",
                        "config": {"slug": "example"},
                    }
                ],
            },
            {
                "name": "Workday Employer",
                "sources": [
                    {
                        "ats": "workday",
                        "official_source_url": "https://example.wd3.myworkdayjobs.com/Careers",
                        "config": {
                            "host_prefix": "example.wd3",
                            "tenant": "example",
                            "site": "Careers",
                        },
                    }
                ],
            },
        ]
    }
    connection = FakeConnection()

    first = import_registry(registry, connection)
    second = import_registry(registry, connection)

    assert first == {"employers_created": 2, "sources_created": 2, "sources_updated": 0}
    assert second == {
        "employers_created": 0,
        "sources_created": 0,
        "sources_updated": 0,
    }


def test_registry_import_rejects_adapters_outside_v1_scope() -> None:
    registry = {
        "employers": [
            {
                "name": "Unsupported",
                "sources": [
                    {"ats": "lever", "official_source_url": "https://jobs.example.com"}
                ],
            }
        ]
    }
    with pytest.raises(ValueError, match="Greenhouse/Workday registry"):
        import_registry(registry, FakeConnection())
