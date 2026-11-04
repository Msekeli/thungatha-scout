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

    def list_for_employer(self, employer_id: UUID) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT * FROM employer_sources
            WHERE employer_id = %s
            ORDER BY created_at, id
            """,
            (employer_id,),
        ).fetchall()
