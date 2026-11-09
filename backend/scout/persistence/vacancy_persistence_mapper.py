from uuid import UUID

from psycopg.types.json import Jsonb

from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy


def map_normalized_vacancy(
    employer_id: UUID,
    source_id: UUID,
    source_url: str,
    vacancy: NormalizedVacancy,
    fingerprint: str,
) -> dict:
    return {
        "employer_id": employer_id,
        "source_id": source_id,
        "external_job_id": vacancy.external_job_id,
        "title": vacancy.title,
        "description": vacancy.description,
        "location_text": vacancy.location_text,
        "department": vacancy.department,
        "office": vacancy.office,
        "source_url": source_url,
        "application_url": vacancy.application_url,
        "published_at": vacancy.published_at,
        "source_updated_at": vacancy.source_updated_at,
        "raw_payload": Jsonb(dict(vacancy.raw_payload)),
        "fingerprint": fingerprint,
    }
