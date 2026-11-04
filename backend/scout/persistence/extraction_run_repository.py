from typing import Any
from uuid import UUID

from psycopg.connection import Connection


class ExtractionRunRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, source_id: UUID) -> UUID:
        row = self._connection.execute(
            """
            INSERT INTO extraction_runs (source_id, outcome)
            VALUES (%s, 'running')
            RETURNING id
            """,
            (source_id,),
        ).fetchone()
        return row["id"]

    def finish(
        self,
        run_id: UUID,
        outcome: str,
        received: int,
        inserted: int,
        updated: int,
        complete: bool,
        detail: str | None,
    ) -> dict[str, Any]:
        return self._connection.execute(
            """
            UPDATE extraction_runs
            SET outcome = %s, finished_at = NOW(), jobs_received = %s,
                jobs_inserted = %s, jobs_updated = %s, complete = %s, detail = %s
            WHERE id = %s
            RETURNING *
            """,
            (outcome, received, inserted, updated, complete, detail, run_id),
        ).fetchone()

    def list_for_source(self, source_id: UUID) -> list[dict[str, Any]]:
        return self._connection.execute(
            """
            SELECT * FROM extraction_runs
            WHERE source_id = %s
            ORDER BY started_at DESC
            LIMIT 20
            """,
            (source_id,),
        ).fetchall()
