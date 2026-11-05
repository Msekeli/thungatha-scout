from registry_importer_test_connection import FakeConnection
from registry_source_test_data import add_source, registry_for
from scout.registry_importer import import_registry


def test_same_source_url_updates_changed_adapter_config() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    source = add_source(connection, "example")

    result = import_registry(
        registry_for(source["source_url"], {"slug": "new"}), connection
    )

    assert result["sources_updated"] == 1
    assert source["adapter_config"] == {"slug": "new"}


def test_single_existing_source_is_reconciled_to_new_url() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    source = add_source(connection, "old")

    result = import_registry(
        registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
        connection,
    )

    assert result["sources_updated"] == 1
    assert source["normalized_url"].endswith("/new")
