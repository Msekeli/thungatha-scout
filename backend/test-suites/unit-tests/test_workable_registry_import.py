from registry_importer_test_connection import FakeConnection

from scout.registry_importer import import_registry


def test_workable_source_is_supported_by_registry_import() -> None:
    registry = {
        "employers": [
            {
                "name": "Workable Employer",
                "careers_url": "https://apply.workable.com/demo/",
                "sources": [
                    {
                        "ats": "workable",
                        "official_source_url": "https://apply.workable.com/demo/",
                        "config": {"slug": "demo"},
                    }
                ],
            }
        ]
    }
    result = import_registry(registry, FakeConnection())
    assert result["employers_created"] == 1
    assert result["sources_created"] == 1
    assert result["sources_skipped"] == 0
