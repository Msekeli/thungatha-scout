from collections.abc import Mapping
from typing import Any

from psycopg.types.json import Jsonb


class EmployerSourceCreateOperations:
    def create(self, values: Mapping[str, Any]) -> dict[str, Any]:
        row = self._connection.execute(
            """
            INSERT INTO employer_sources (
                employer_id, adapter_key, source_url, employer_careers_url,
                normalized_url, adapter_config, status, permission_status,
                relationship_evidence
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

    def update_configuration(
        self, employer_id: Any, source_id: Any, values: Mapping[str, Any]
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employer_sources
            SET source_url = %s, normalized_url = %s,
                adapter_config = %s, updated_at = NOW()
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
