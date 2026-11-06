import re
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)

_OFFICE_SUFFIX = re.compile(
    r"\\s+(?:dc|office|hub|distribution centre|distribution center|"
    r"cross dock facility|facility|warehouse)$",
    re.IGNORECASE,
)
_BROAD_LOCATIONS = {
    "south africa", "western cape", "eastern cape", "northern cape",
    "gauteng", "kwazulu natal", "kwa zulu natal", "free state",
    "north west", "limpopo", "mpumalanga",
}


def _office_location_names(offices: Any) -> list[str]:
    if not isinstance(offices, list):
        return []
    names: list[str] = []
    for office in offices:
        if not isinstance(office, dict) or not isinstance(office.get("name"), str):
            continue
        name = office["name"].strip()
        if not name:
            continue
        canonical = _OFFICE_SUFFIX.sub("", name).strip(" ,-/")
        if canonical and canonical.casefold() not in {"head", "main", "regional", "national"}:
            if canonical.casefold() not in {item.casefold() for item in names}:
                names.append(canonical)
    return names


def _resolve_location_text(location: Any, offices: Any) -> str | None:
    location_name = (
        location.get("name").strip()
        if isinstance(location, dict) and isinstance(location.get("name"), str)
        else location.strip() if isinstance(location, str) else ""
    )
    office_names = _office_location_names(offices)
    if office_names and (
        not location_name or location_name.casefold() in _BROAD_LOCATIONS
    ):
        return " | ".join(office_names)
    if location_name:
        return location_name
    return " | ".join(office_names) if office_names else None


def map_greenhouse_job(
    employer_id: UUID,
    source_id: UUID,
    source_url: str,
    job: Mapping[str, Any],
    fingerprint: str,
) -> dict[str, Any]:
    departments = job.get("departments")
    offices = job.get("offices")
    office_names = (
        [item.get("name") for item in offices
         if isinstance(item, dict) and isinstance(item.get("name"), str)]
        if isinstance(offices, list) else []
    )
    return {
        "employer_id": employer_id,
        "source_id": source_id,
        "external_job_id": str(job["id"]),
        "title": job["title"].strip(),
        "description": sanitize_vacancy_description(job.get("content")),
        "location_text": _resolve_location_text(job.get("location"), offices),
        "department": departments[0].get("name")
        if isinstance(departments, list)
        and departments
        and isinstance(departments[0], dict)
        else None,
        "office": office_names[0] if office_names else None,
        "source_url": source_url,
        "application_url": job["absolute_url"],
        "published_at": job.get("first_published"),
        "source_updated_at": job.get("updated_at"),
        "raw_payload": Jsonb({
            key: job[key]
            for key in ("location", "departments", "offices")
            if key in job
        }),
        "fingerprint": fingerprint,
    }
