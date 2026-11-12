from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy


def map_workday_vacancy(
    listing: Mapping[str, Any], detail: Mapping[str, Any], host: str, site: str,\n    locale: str = "en-US"
) -> NormalizedVacancy:
    info = detail["jobPostingInfo"]
    path = required_text(listing, "externalPath")
    identifier = info.get("jobReqId") or _bullet_id(listing) or path.rsplit("/", 1)[-1]
    title = info.get("title") or listing.get("title")
    if not isinstance(identifier, str) or not identifier.strip():
        raise ValueError("Workday vacancy has no stable identifier.")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("Workday vacancy has no title.")
    apply_url = info.get("externalUrl")
    if not _https_url(apply_url):
        apply_url = f"https://{host}/{locale}/{site}{path}"
    location = info.get("location") or listing.get("locationsText")
    locations = info.get("additionalLocations")
    if isinstance(locations, list):
        names = [_location(item) for item in locations]
        extras = [name for name in names if name]
        if extras:
            location = (
                "; ".join(dict.fromkeys([str(location), *extras]))
                if location
                else "; ".join(extras)
            )
    department = info.get("jobFamily") or info.get("jobFamilyGroup")
    raw = {**dict(listing), **dict(detail), "application_url": apply_url}
    return NormalizedVacancy(
        external_job_id=identifier.strip(),
        title=title.strip(),
        description=sanitize_vacancy_description(info.get("jobDescription")),
        location_text=location.strip()
        if isinstance(location, str) and location.strip()
        else None,
        department=department if isinstance(department, str) else None,
        office=None,
        application_url=apply_url,
        published_at=None,
        source_updated_at=None,
        raw_payload=raw,
    )


def required_text(value: Mapping[str, Any], field: str) -> str:
    item = value.get(field)
    if not isinstance(item, str) or not item.strip():
        raise ValueError(f"Workday vacancy is missing {field}.")
    return item.strip()


def _bullet_id(listing: Mapping[str, Any]) -> str | None:
    bullets = listing.get("bulletFields")
    return (
        bullets[0]
        if isinstance(bullets, list) and bullets and isinstance(bullets[0], str)
        else None
    )


def _location(value: Any) -> str | None:
    if isinstance(value, str):
        return value.strip() or None
    if isinstance(value, dict):
        return value.get("descriptor") or value.get("location")
    return None


def _https_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlsplit(value)
    return parsed.scheme == "https" and bool(parsed.hostname)
