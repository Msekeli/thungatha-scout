import hashlib
import json
from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection
from psycopg.types.json import Jsonb


class VacancyRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

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
            values = self._values(
                employer_id, source_id, source_url, job, fingerprint
            )
            row = self._connection.execute(
                """
                INSERT INTO vacancies (
                    employer_id, source_id, external_job_id, title, description,
                    location_text, department, office, source_url, application_url,
                    source_updated_at, raw_payload, content_fingerprint
                )
                VALUES (
                    %(employer_id)s, %(source_id)s, %(external_job_id)s,
                    %(title)s, %(description)s, %(location_text)s, %(department)s,
                    %(office)s, %(source_url)s, %(application_url)s,
                    %(source_updated_at)s, %(raw_payload)s, %(fingerprint)s
                )
                ON CONFLICT (source_id, external_job_id) DO UPDATE SET
                    title = EXCLUDED.title,
                    description = EXCLUDED.description,
                    location_text = EXCLUDED.location_text,
                    department = EXCLUDED.department,
                    office = EXCLUDED.office,
                    application_url = EXCLUDED.application_url,
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
        location = job.get("location")
        departments = job.get("departments")
        offices = job.get("offices")
        return {
            "employer_id": employer_id,
            "source_id": source_id,
            "external_job_id": str(job["id"]),
            "title": job["title"].strip(),
            "description": job.get("content"),
            "location_text": location.get("name") if isinstance(location, dict) else None,
            "department": departments[0].get("name") if isinstance(departments, list) and departments and isinstance(departments[0], dict) else None,
            "office": offices[0].get("name") if isinstance(offices, list) and offices and isinstance(offices[0], dict) else None,
            "source_url": source_url,
            "application_url": job["absolute_url"],
            "source_updated_at": job.get("updated_at"),
            "raw_payload": Jsonb(dict(job)),
            "fingerprint": fingerprint,
        }

    def list_for_employer(
        self, employer_id: UUID, limit: int = 200, offset: int = 0
    ) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.employer_id = %s AND v.status = 'active'
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (employer_id, limit, offset),
        ).fetchall()

    def list_all(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.status = 'active'
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()
