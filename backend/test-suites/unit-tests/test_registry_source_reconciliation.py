import pytest

from registry_importer_test_connection import FakeConnection
from scout.registry_importer import import_registry


def registry_for(url: str, config: dict) -> dict:
    return {
        "employers": [
            {
                "name": "Example Employer",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": url,
                        "config": config,
                    }
                ],
            }
        ]
    }


def source_row(connection: FakeConnection, slug: str) -> dict:
    employer_id = connection.employers[0]["id"]
    url = f"https://job-boards.greenhouse.io/{slug}"
    row = {
        "id": slug,
        "employer_id": employer_id,
        "adapter_key": "greenhouse",
        "source_url": url,
        "normalized_url": url,
        "adapter_config": {"slug": slug},
        "status": "discovered",
        "permission_status": "unknown",
    }
    connection.sources.append(row)
    return row


def test_same_source_url_updates_changed_adapter_config() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    source = source_row(connection, "example")

    result = import_registry(
        registry_for(source["source_url"], {"slug": "new"}), connection
    )

    assert result["sources_updated"] == 1
    assert source["adapter_config"] == {"slug": "new"}


def test_single_existing_source_is_reconciled_to_new_url() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    source = source_row(connection, "old")

    result = import_registry(
        registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
        connection,
    )

    assert result["sources_updated"] == 1
    assert source["normalized_url"].endswith("/new")


def test_multiple_existing_sources_are_not_reconciled_automatically() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    source_row(connection, "old-one")
    source_row(connection, "old-two")

    with pytest.raises(ValueError, match="Cannot safely reconcile multiple"):
        import_registry(
            registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
            connection,
        )


def test_source_assigned_to_another_employer_is_rejected() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "First"}]}, connection)
    first_source = source_row(connection, "shared")
    import_registry({"employers": [{"name": "Second"}]}, connection)
    registry = {
        "employers": [
            {
                "name": "Second",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": first_source["source_url"],
                        "config": {"slug": "shared"},
                    }
                ],
            }
        ]
    }

    with pytest.raises(ValueError, match="assigned elsewhere"):
        import_registry(registry, connection)
