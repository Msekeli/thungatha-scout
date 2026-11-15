import pytest

from registry_importer_test_connection import FakeConnection
from scout.registry_importer import import_registry
from scout.registry_loader import RegistryValidationError


def test_new_source_is_registered_without_verification_state() -> None:
    connection = FakeConnection()
    registry = {
        "employers": [
            {
                "name": "Example Employer",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/example",
                        "config": {"slug": "example"},
                    }
                ],
            }
        ]
    }

    result = import_registry(registry, connection)

    assert result["sources_created"] == 1
    source = connection.sources[0]
    assert source["adapter_config"] == {"slug": "example"}
    assert "status" not in source
    assert "permission_status" not in source


def test_source_import_rejects_missing_required_adapter_config() -> None:
    registry = {
        "employers": [
            {
                "name": "Example Employer",
                "sources": [
                    {
                        "ats": "greenhouse",
                        "official_source_url": "https://job-boards.greenhouse.io/example",
                        "config": {},
                    }
                ],
            }
        ]
    }
    with pytest.raises(RegistryValidationError, match="slug"):
        import_registry(registry, FakeConnection())
