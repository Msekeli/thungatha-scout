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
        raise RegistryValidationError(
            "ATS adapter registry cannot be loaded."
        ) from exception

    adapters = registry.get("adapters") if isinstance(registry, dict) else None
    if not isinstance(adapters, dict) or not adapters:
        raise RegistryValidationError(
            "ATS adapter registry has no adapter definitions."
        )
    for key, definition in adapters.items():
        if not isinstance(definition, dict):
            raise RegistryValidationError(f"Adapter '{key}' must be an object.")
        schema = definition.get("config_schema") or definition.get("config")
        if not isinstance(schema, list):
            raise RegistryValidationError(f"Adapter '{key}' has no config schema.")
        definition["config_schema"] = schema
        if "extraction_method" not in definition and "retrieval" in definition:
            retrieval = definition["retrieval"]
            if retrieval == "observed_public_cxs_json":
                retrieval = "observed_public_cxs_json_post"
            definition["extraction_method"] = retrieval
        if key == "lever" and "config_values" not in definition:
            definition["config_values"] = {"region": ["global", "eu"]}
    return adapters


def validate_source_config(adapter_key: str, config: dict[str, Any]) -> None:
    adapters = load_adapter_registry()
    definition = adapters.get(adapter_key)
    if definition is None:
        raise RegistryValidationError(f"Unknown adapter: {adapter_key}.")

    required = definition["config_schema"]
    missing = [
        field
        for field in required
        if not isinstance(config.get(field), str) or not config[field].strip()
    ]
    if missing:
        fields = ", ".join(missing)
        raise RegistryValidationError(
            f"Adapter '{adapter_key}' is missing configuration: {fields}."
        )
    for field, allowed_values in definition.get("config_values", {}).items():
        if config.get(field) not in allowed_values:
            choices = ", ".join(allowed_values)
            raise RegistryValidationError(
                f"Adapter '{adapter_key}' field '{field}' must be one of: {choices}."
            )
