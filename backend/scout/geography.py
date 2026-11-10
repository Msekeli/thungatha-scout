import re
from collections.abc import Mapping
from typing import Any

from scout.south_african_location_terms import SOUTH_AFRICAN_LOCATION_TERMS

_NORMALIZE = re.compile(r"[^a-z0-9]+")


def is_south_african_location(location: str | None) -> bool:
    evidence = _NORMALIZE.sub(" ", location.lower() if location else "").strip()
    return bool(evidence) and any(
        re.search(rf"(^| ){re.escape(term)}( |$)", evidence)
        for term in SOUTH_AFRICAN_LOCATION_TERMS
    )


def vacancy_location_evidence(job: Mapping[str, Any]) -> str:
    parts: list[str] = []
    location = job.get("location")
    if isinstance(location, Mapping):
        parts.append(_text(location.get("name")))
    elif isinstance(location, str):
        parts.append(_text(location))
    offices = job.get("offices")
    if isinstance(offices, list):
        for office in offices:
            if isinstance(office, Mapping):
                parts.append(_text(office.get("name")))
    return " ".join(part for part in parts if part)


def _text(value: Any) -> str:
    return value.strip().lower() if isinstance(value, str) else ""


def is_south_african_vacancy(job: Mapping[str, Any]) -> bool:
    return is_south_african_location(vacancy_location_evidence(job))
