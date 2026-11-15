from registry_importer_test_connection import FakeConnection

from scout.registry_importer import import_registry


def test_registry_import_updates_careers_url_on_existing_source() -> None:
    registry = {
        "employers": [
            {
                "name": "Mama Money",
                "website_url": "https://www.mamamoney.co.za/",
                "careers_url": None,
                "sources": [
                    {
                        "ats": "lever",
                        "official_source_url": "https://jobs.lever.co/mamamoney",
                        "config": {"slug": "mamamoney", "region": "global"},
                    }
                ],
            }
        ]
    }
    connection = FakeConnection()
    import_registry(registry, connection)
    registry["employers"][0]["careers_url"] = "https://jobs.lever.co/mamamoney"
    result = import_registry(registry, connection)
    assert result["sources_updated"] == 1
    assert connection.employers[0]["website_url"] == "https://www.mamamoney.co.za/"
    assert connection.sources[0]["employer_careers_url"] == (
        "https://jobs.lever.co/mamamoney"
    )
