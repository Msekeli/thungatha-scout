from collections.abc import Mapping
from typing import Any

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy
from .greenhouse_vacancy_location_mapper import resolve_greenhouse_location


def map_greenhouse_job(job: Mapping[str, Any]) -> NormalizedVacancy:
    departments = job.get("departments")
    offices = job.get("offices")
    office_names = (
        [
            item.get("name")
            for item in offices
            if isinstance(item, dict) and isinstance(item.get("name"), str)
        ]
        if isinstance(offices, list)
        else []
    )
    department = (
        departments[0].get("name")
        if isinstance(departments, list)
        and departments
        and isinstance(departments[0], dict)
        else None
    )
    return NormalizedVacancy(
        external_job_id=str(job["id"]),
        title=job["title"].strip(),
        description=sanitize_vacancy_description(job.get("content")),
        location_text=resolve_greenhouse_location(job.get("location"), offices),
        department=department,
        office=office_names[0] if office_names else None,
        application_url=job["absolute_url"],
        published_at=job.get("first_published"),
        source_updated_at=job.get("updated_at"),
        raw_payload=dict(job),
    )
