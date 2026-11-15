from typing import Any

from scout.application.employer_contracts import EmployerSourceCreate


def source_create_values(payload: EmployerSourceCreate) -> dict[str, Any]:
    values = payload.model_dump()
    if payload.discovery_preview is not None:
        values["discovery_preview"] = payload.discovery_preview.model_dump(mode="json")
    for key in ("source_url", "normalized_url"):
        values[key] = str(values[key])
    if values["employer_careers_url"] is not None:
        values["employer_careers_url"] = str(values["employer_careers_url"])
    return values
