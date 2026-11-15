from collections.abc import Mapping
from typing import Any
from urllib.parse import urlsplit

from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy
from scout.ats_adapters.workable_adapter.workable_description_parser import (
    extract_workable_description,
)


def map_workable_job(job: Mapping[str, Any]) -> NormalizedVacancy:
    job_id = required_text(job, "shortcode")
    title = required_text(job, "title")
    application_url = required_https_url(job, "url")
    location = [
        job.get(field)
        for field in ("city", "state", "country")
        if isinstance(job.get(field), str) and job[field].strip()
    ]
    department = job.get("department")
    published = job.get("published_on")
    return NormalizedVacancy(
        external_job_id=job_id,
        title=title,
        description=extract_workable_description(job.get("description")),
        location_text=", ".join(location) or None,
        department=department if isinstance(department, str) else None,
        office=None,
        application_url=application_url,
        published_at=published if isinstance(published, str) else None,
        source_updated_at=None,
        raw_payload=dict(job),
    )


def required_text(job: Mapping[str, Any], field: str) -> str:
    value = job.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Workable job is missing {field}.")
    return value.strip()


def required_https_url(job: Mapping[str, Any], field: str) -> str:
    value = required_text(job, field)
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError(f"Workable job {field} must be an absolute HTTPS URL.")
    return value
