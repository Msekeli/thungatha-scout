import pytest

from registry_importer_test_connection import FakeConnection
from registry_source_test_data import add_source, registry_for
from scout.registry_importer import import_registry


def test_multiple_existing_sources_are_not_reconciled_automatically() -> None:
    connection = FakeConnection()
    import_registry(
        registry_for("https://job-boards.greenhouse.io/old-one", {"slug": "old-one"}),
        connection,
    )
    add_source(connection, "old-two")
    with pytest.raises(ValueError, match="Cannot safely reconcile multiple"):
        import_registry(
            registry_for("https://job-boards.greenhouse.io/new", {"slug": "new"}),
            connection,
        )


def test_source_assigned_to_another_employer_is_rejected() -> None:
    connection = FakeConnection()
    import_registry(
        registry_for("https://job-boards.greenhouse.io/shared", {"slug": "shared"}),
        connection,
    )
    first_source = connection.sources[0]
    import_registry(
        {
            "employers": [
                {
                    "name": "Second",
                    "sources": [
                        {
                            "ats": "greenhouse",
                            "official_source_url": "https://job-boards.greenhouse.io/second",
                            "config": {"slug": "second"},
                        }
                    ],
                }
            ]
        },
        connection,
    )
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
