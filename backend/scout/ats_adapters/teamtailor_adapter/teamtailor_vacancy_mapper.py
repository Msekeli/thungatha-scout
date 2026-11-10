from collections.abc import Mapping
from datetime import timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlsplit

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy


def map_teamtailor_job(job: Mapping[str, Any]) -> NormalizedVacancy:
    identifier, title, link = job.get("guid"), job.get("title"), job.get("link")
    if not all(
        isinstance(value, str) and value.strip() for value in (identifier, title, link)
    ):
        raise ValueError("Teamtailor vacancy requires a GUID, title and advert URL.")
    parsed = urlsplit(link)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Teamtailor advert URL must be an absolute HTTPS URL.")
    locations = job.get("locations")
    locations = locations if isinstance(locations, list) else []
    names = [_location_name(item) for item in locations if isinstance(item, dict)]
    location_text = "; ".join(dict.fromkeys(name for name in names if name)) or None
    department = job.get("department")
    description = sanitize_vacancy_description(job.get("description"))
    return NormalizedVacancy(
        external_job_id=identifier.strip(),
        title=title.strip(),
        description=description or None,
        location_text=location_text,
        department=department.strip()
        if isinstance(department, str) and department.strip()
        else None,
        office=names[0] if names else None,
        application_url=link,
        published_at=_publication_date(job.get("pubDate")),
        source_updated_at=None,
        raw_payload=dict(job),
    )


def _location_name(location: dict[str, Any]) -> str | None:
    name = location.get("name")
    if isinstance(name, str) and name.strip():
        return name.strip()
    parts = [location.get(key) for key in ("city", "country")]
    values = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
    return ", ".join(values) or None


def _publication_date(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).isoformat()
