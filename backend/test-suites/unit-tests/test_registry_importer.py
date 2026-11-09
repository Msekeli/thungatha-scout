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


def test_registry_import_skips_unsupported_only_employers() -> None:
    registry = {
        "employers": [
            {
                "name": "Network Recruitment",
                "organization_classification": "recruitment_agency",
                "sources": [
                    {
                        "ats": "placement_partner",
                        "official_source_url": "https://placementpartner.co.za/live/agency.php?agency=network",
                        "config": {"agency_id": "network"},
                    }
                ],
            }
        ]
    }
    result = import_registry(registry, FakeConnection())
    assert result["employers_created"] == 0
    assert result["sources_created"] == 0
    assert result["sources_skipped"] == 1


def test_registry_import_updates_careers_url_on_existing_source() -> None:
    registry = {
        "employers": [{
            "name": "Mama Money",
            "careers_url": None,
            "sources": [{
                "ats": "lever",
                "official_source_url": "https://jobs.lever.co/mamamoney",
                "config": {"slug": "mamamoney", "region": "global"},
            }],
        }]
    }
    connection = FakeConnection()
    import_registry(registry, connection)
    registry["employers"][0]["careers_url"] = "https://www.mamamoney.co.za/"
    result = import_registry(registry, connection)
    assert result["sources_updated"] == 1
    assert connection.sources[0]["employer_careers_url"] == "https://www.mamamoney.co.za/"
