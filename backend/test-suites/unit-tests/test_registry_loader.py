import pytest

from scout.registry_loader import (
    RegistryValidationError,
    load_adapter_registry,
    validate_source_config,
)


def test_adapter_registry_contains_greenhouse_and_workday() -> None:
    adapters = load_adapter_registry()

    assert adapters["greenhouse"]["extraction_method"] == "documented_public_json_api"
    assert adapters["workday"]["extraction_method"] == "observed_public_cxs_json_post"


def test_greenhouse_source_requires_slug() -> None:
    with pytest.raises(RegistryValidationError, match="slug"):
        validate_source_config("greenhouse", {})


def test_workday_source_requires_host_tenant_and_site() -> None:
    with pytest.raises(RegistryValidationError, match="host_prefix"):
        validate_source_config("workday", {"tenant": "tenant", "site": "site"})


def test_registry_rejects_unknown_adapter() -> None:
    with pytest.raises(RegistryValidationError, match="Unknown adapter"):
        validate_source_config("unknown", {})

def test_lever_source_requires_slug_and_region() -> None:
    with pytest.raises(RegistryValidationError, match="slug, region"):
        validate_source_config("lever", {"slug": "mamamoney"})

    validate_source_config("lever", {"slug": "mamamoney", "region": "global"})
