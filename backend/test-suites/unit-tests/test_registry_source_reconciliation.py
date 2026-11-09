from registry_importer_test_connection import FakeConnection
from registry_source_test_data import registry_for
from scout.registry_importer import import_registry


def test_same_source_url_updates_changed_adapter_config() -> None:
    connection = FakeConnection()
    source_url = "https://job-boards.greenhouse.io/example"
    import_registry(registry_for(source_url, {"slug": "example"}), connection)
    source = connection.sources[0]
    result = import_registry(registry_for(source_url, {"slug": "new"}), connection)
    assert result["sources_updated"] == 1
    assert source["adapter_config"] == {"slug": "new"}


def test_single_existing_source_is_reconciled_to_new_url() -> None:
    connection = FakeConnection()
    import_registry(
        registry_for("https://job-boards.greenhouse.io/old", {"slug": "old"}),
        connection,
    )
    source = connection.sources[0]
    result = import_registry(
        registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
        connection,
    )
    assert result["sources_updated"] == 1
    assert source["normalized_url"].endswith("/new")
