from registry_importer_test_connection import FakeConnection

from scout.registry_importer import import_registry


def test_registry_import_can_be_limited_to_one_adapter() -> None:
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
    result = import_registry(registry, connection, adapter_key="workday")

    assert result["employers_created"] == 1
    assert result["sources_created"] == 1
    assert result["sources_skipped"] == 0
    assert [item["name"] for item in connection.employers] == ["Workday Employer"]
    assert [item["adapter_key"] for item in connection.sources] == ["workday"]
