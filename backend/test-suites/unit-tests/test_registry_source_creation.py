from scout.registry_importer import import_registry
from registry_importer_test_connection import FakeConnection


def test_new_source_is_discovered_and_permission_remains_unknown() -> None:
    connection = FakeConnection()
    registry = {"employers": [{
        "name": "Example Employer",
        "sources": [{
            "ats": "greenhouse",
            "official_source_url": "https://job-boards.greenhouse.io/example",
            "config": {"slug": "example"},
            "verification_evidence": ["https://example.com/careers"],
        }],
    }]}

    result = import_registry(registry, connection)

    assert result["sources_created"] == 1
    source = connection.sources[0]
    assert source["status"] == "discovered"
    assert source["permission_status"] == "unknown"
    assert source["relationship_evidence"] == [{
        "url": "https://example.com/careers", "status": "claimed"
    }]
