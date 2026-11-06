from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb

from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)
from scout.persistence.vacancy_location_mapping import resolve_greenhouse_location


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
        "location_text": resolve_greenhouse_location(job.get("location"), offices),
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
