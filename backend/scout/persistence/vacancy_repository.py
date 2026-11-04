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
        location = job.get("location")
        location_name = location.get("name") if isinstance(location, dict) else None
        location_text = location_name if isinstance(location_name, str) else None
        location_normalized = location_text.lower() if location_text else ""
        departments = job.get("departments")
        offices = job.get("offices")
        return {
            "employer_id": employer_id,
            "source_id": source_id,
            "external_job_id": str(job["id"]),
            "title": job["title"].strip(),
            "description": job.get("content"),
            "location_text": location_text,
            "department": departments[0].get("name") if isinstance(departments, list) and departments and isinstance(departments[0], dict) else None,
            "office": offices[0].get("name") if isinstance(offices, list) and offices and isinstance(offices[0], dict) else None,
            "source_url": source_url,
            "application_url": job["absolute_url"],
            "published_at": job.get("first_published"),
            "source_updated_at": job.get("updated_at"),
            "raw_payload": Jsonb(dict(job)),
            "fingerprint": fingerprint,
            "review_status": (
                "needs_verification"
                if not location_text
                or any(term in location_normalized for term in ("south africa", "remote"))
                else "pending"
            ),
            "review_reason": (
                "Location is missing from the source."
                if not location_text
                else "Verify the stated South African or remote-work location and eligibility."
                if any(term in location_normalized for term in ("south africa", "remote"))
                else None
            ),
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
              AND v.archived_at IS NULL
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
            WHERE v.status = 'active' AND v.archived_at IS NULL
            ORDER BY v.source_updated_at DESC NULLS LAST, v.created_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()


    def get_by_id(self, vacancy_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name,
                   e.logo_url AS employer_logo_url,
                   e.logo_source_url AS employer_logo_source_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.id = %s
            """,
            (vacancy_id,),
        ).fetchone()

    def update_review(
        self, vacancy_id: UUID, review_status: str, review_reason: str | None
    ) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            UPDATE vacancies
            SET review_status = %s,
                review_reason = %s,
                reviewed_at = CASE WHEN %s = 'verified' THEN NOW() ELSE NULL END,
                updated_at = NOW()
            WHERE id = %s AND archived_at IS NULL
            RETURNING id
            """,
            (review_status, review_reason, review_status, vacancy_id),
        ).fetchone()
        return self.get_by_id(vacancy_id) if row else None

    def archive(
        self, vacancy_id: UUID, reason: str | None = None
    ) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            UPDATE vacancies
            SET archived_at = NOW(), archived_reason = %s, updated_at = NOW()
            WHERE id = %s AND archived_at IS NULL
            RETURNING id
            """,
            (reason, vacancy_id),
        ).fetchone()
        return self.get_by_id(vacancy_id) if row else None

    def restore(self, vacancy_id: UUID) -> dict[str, Any] | None:
        row = self._connection.execute(
            """
            UPDATE vacancies
            SET archived_at = NULL, archived_reason = NULL, updated_at = NOW()
            WHERE id = %s AND archived_at IS NOT NULL
            RETURNING id
            """,
            (vacancy_id,),
        ).fetchone()
        return self.get_by_id(vacancy_id) if row else None


    def list_archived(self, limit: int = 200, offset: int = 0) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name,
                   e.logo_url AS employer_logo_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.archived_at IS NOT NULL
            ORDER BY v.archived_at DESC
            LIMIT %s OFFSET %s
            """,
            (limit, offset),
        ).fetchall()
