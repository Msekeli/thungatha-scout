import hashlib
import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb


class VacancyIngestionOperations:
    def upsert_batch(
        self,
        employer_id: UUID,
        source_id: UUID,
        source_url: str,
        jobs: list[dict[str, Any]],
    ) -> tuple[int, int]:
        inserted = updated = 0
        for job in jobs:
            raw = json.dumps(job, sort_keys=True, separators=(",", ":"))
            fingerprint = hashlib.sha256(raw.encode()).hexdigest()
            values = self._values(employer_id, source_id, source_url, job, fingerprint)
            row = self._connection.execute(
                """
                INSERT INTO vacancies (
                    employer_id, source_id, external_job_id, title, description,
                    location_text, department, office, source_url, application_url,
                    published_at, source_updated_at, raw_payload, content_fingerprint,
                    review_status, review_reason
                )
                VALUES (
                    %(employer_id)s, %(source_id)s, %(external_job_id)s,
                    %(title)s, %(description)s, %(location_text)s, %(department)s,
                    %(office)s, %(source_url)s, %(application_url)s,
                    %(published_at)s, %(source_updated_at)s, %(raw_payload)s, %(fingerprint)s,
                    %(review_status)s, %(review_reason)s
                )
                ON CONFLICT (source_id, external_job_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    location_text = EXCLUDED.location_text,
                    department = EXCLUDED.department,
                    office = EXCLUDED.office,
                    application_url = EXCLUDED.application_url,
                    published_at = EXCLUDED.published_at,
                    source_updated_at = EXCLUDED.source_updated_at,
                    raw_payload = EXCLUDED.raw_payload,
                    content_fingerprint = EXCLUDED.content_fingerprint,
                    last_seen_at = NOW(),
                    last_checked_at = NOW(),
                    status = 'active',
                    updated_at = NOW()
                RETURNING (xmax = 0) AS inserted
                """,
                values,
            ).fetchone()
            if row["inserted"]:
                inserted += 1
            else:
                updated += 1
        return inserted, updated

    @staticmethod
    def _values(
        employer_id: UUID,
        source_id: UUID,
        source_url: str,
        job: Mapping[str, Any],
        fingerprint: str,
    ) -> dict[str, Any]:
        from scout.persistence.vacancy_payload_mapper import map_greenhouse_job

        return map_greenhouse_job(
            employer_id, source_id, source_url, job, fingerprint
        )
