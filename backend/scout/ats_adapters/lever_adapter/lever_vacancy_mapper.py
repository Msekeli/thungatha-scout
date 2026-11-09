from collections.abc import Mapping
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy
from scout.ats_adapters.lever_adapter.lever_description_parser import (
    extract_lever_description,
)


def map_lever_posting(job: Mapping[str, Any]) -> NormalizedVacancy:
    categories = job.get("categories")
    categories = categories if isinstance(categories, dict) else {}
    locations = categories.get("allLocations")
    if not isinstance(locations, list) or not locations:
        locations = [categories.get("location")]
    location_text = (
        ", ".join(
            value.strip()
            for value in locations
            if isinstance(value, str) and value.strip()
        )
        or None
    )
    department = categories.get("department")
    description = extract_lever_description(
        job.get("descriptionPlain"), job.get("description")
    )
    application_url = job.get("applyUrl")
    hosted_url = job.get("hostedUrl")
    title = job.get("text")
    job_id = job.get("id")
    required = (job_id, title, application_url, hosted_url)
    if not all(isinstance(value, str) and value.strip() for value in required):
        raise ValueError("Lever posting is missing its ID, title or job URLs.")
    if not application_url.startswith(("https://", "http://")):
        raise ValueError("Lever application URL must be absolute.")
    if not hosted_url.startswith(("https://", "http://")):
        raise ValueError("Lever hosted URL must be absolute.")
    return NormalizedVacancy(
        external_job_id=job_id,
        title=title.strip(),
        description=description,
        location_text=location_text,
        department=department if isinstance(department, str) else None,
        office=None,
        application_url=application_url,
        published_at=None,
        source_updated_at=None,
        raw_payload=dict(job),
    )
