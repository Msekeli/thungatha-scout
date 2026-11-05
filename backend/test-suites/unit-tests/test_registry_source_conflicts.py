import pytest

from registry_importer_test_connection import FakeConnection
from registry_source_test_data import add_source, registry_for
from scout.registry_importer import import_registry


def test_multiple_existing_sources_are_not_reconciled_automatically() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "Example Employer"}]}, connection)
    add_source(connection, "old-one")
    add_source(connection, "old-two")

    with pytest.raises(ValueError, match="Cannot safely reconcile multiple"):
        import_registry(
            registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
            connection,
        )


def test_source_assigned_to_another_employer_is_rejected() -> None:
    connection = FakeConnection()
    import_registry({"employers": [{"name": "First"}]}, connection)
    first_source = add_source(connection, "shared")
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
