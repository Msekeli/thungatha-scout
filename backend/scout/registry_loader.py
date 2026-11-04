import json
from pathlib import Path
from typing import Any

REGISTRY_DIRECTORY = Path(__file__).resolve().parents[1] / "registry"


class RegistryValidationError(ValueError):
    """Raised when a checked-in registry is inconsistent or malformed."""


def load_adapter_registry() -> dict[str, Any]:
    path = REGISTRY_DIRECTORY / "ats-adapter-registry.json"
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exception:
        raise RegistryValidationError("ATS adapter registry cannot be loaded.") from exception

    adapters = registry.get("adapters") if isinstance(registry, dict) else None
    if not isinstance(adapters, dict) or not adapters:
        raise RegistryValidationError("ATS adapter registry has no adapter definitions.")
    for key, definition in adapters.items():
        if not isinstance(definition, dict):
            raise RegistryValidationError(f"Adapter '{key}' must be an object.")
        if not isinstance(definition.get("config_schema"), list):
            raise RegistryValidationError(f"Adapter '{key}' has no config schema.")
    return adapters


def validate_source_config(adapter_key: str, config: dict[str, Any]) -> None:
    adapters = load_adapter_registry()
    definition = adapters.get(adapter_key)
    if definition is None:
        raise RegistryValidationError(f"Unknown adapter: {adapter_key}.")

    required = definition["config_schema"]
    missing = [
        field for field in required
        if field not in config or config[field] in (None, "")
    ]
    if missing:
        raise RegistryValidationError(
            f"Adapter '{adapter_key}' is missing configuration: {', '.join(missing)}."
        )
