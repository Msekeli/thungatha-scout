from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection
from psycopg.types.json import Jsonb


class EmployerSourceRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, values: Mapping[str, Any]) -> dict[str, Any]:
        row = self._connection.execute(
            """
            INSERT INTO employer_sources (
                employer_id, adapter_key, source_url, employer_careers_url,
                normalized_url,
                adapter_config, status, permission_status, relationship_evidence
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING *
            """,
            (
                values["employer_id"],
                values["adapter_key"],
                values["source_url"],
                values.get("employer_careers_url"),
                values["normalized_url"],
                Jsonb(values.get("adapter_config", {})),
                values["status"],
                values["permission_status"],
                Jsonb(values.get("relationship_evidence", [])),
            ),
        ).fetchone()
        return row

    def get_by_id(self, source_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute(
            "SELECT * FROM employer_sources WHERE id = %s",
            (source_id,),
        ).fetchone()

    def update_configuration(
        self,
        employer_id: UUID,
        source_id: UUID,
        values: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employer_sources
            SET source_url = %s,
                normalized_url = %s,
                adapter_config = %s,
                updated_at = NOW()
            WHERE employer_id = %s AND id = %s AND adapter_key = %s
            RETURNING *
            """,
            (
                values["source_url"],
                values["normalized_url"],
                Jsonb(values["adapter_config"]),
                employer_id,
                source_id,
                values["adapter_key"],
            ),
        ).fetchone()

    def list_for_employer(self, employer_id: UUID) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT * FROM employer_sources
            WHERE employer_id = %s
            ORDER BY created_at, id
            """,
            (employer_id,),
        ).fetchall()

    def update_review(
        self,
        employer_id: UUID,
        source_id: UUID,
        values: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employer_sources
            SET status = %s,
                permission_status = %s,
                relationship_evidence = relationship_evidence || jsonb_build_array(
                    jsonb_build_object(
                        'evidence_url', %s,
                        'decision_reason', %s,
                        'recorded_at', NOW()
                    )
                ),
                verified_at = CASE WHEN %s = 'verified' THEN NOW()
                    WHEN %s <> 'verified' THEN NULL ELSE verified_at END,
                last_checked_at = NOW(),
                updated_at = NOW()
            WHERE employer_id = %s AND id = %s
            RETURNING *
            """,
            (
                values["status"], values["permission_status"],
                values.get("evidence_url") or None, values.get("reason") or None,
                values["status"], values["status"], employer_id, source_id,
            ),
        ).fetchone()
