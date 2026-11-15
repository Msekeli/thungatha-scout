from typing import Any
from uuid import UUID

from psycopg.connection import Connection


class ExtractionRunRepository:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def create(self, source_id: UUID) -> UUID:
        row = self._connection.execute(
            "INSERT INTO extraction_runs (source_id, outcome) "
            "VALUES (%s, 'running') RETURNING id",
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
        run = self._connection.execute(
            "SELECT source_id, started_at FROM extraction_runs "
            "WHERE id = %s FOR UPDATE",
            (run_id,),
        ).fetchone()
        successful = complete and outcome in ("success", "empty")
        previous = self._connection.execute(
            "SELECT EXISTS (SELECT 1 FROM extraction_runs "
            "WHERE source_id = %s AND id <> %s AND complete = TRUE "
            "AND outcome IN ('success', 'empty') "
            "AND COALESCE(detail, '') NOT LIKE "
            "'Matched registered %% delegated extraction.') AS exists",
            (run["source_id"], run_id),
        ).fetchone()["exists"]
        baseline = successful and not previous
        missing = 0
        if successful and previous:
            rows = self._connection.execute(
                "UPDATE vacancies SET status = 'possibly_expired', updated_at = NOW() "
                "WHERE source_id = %s AND status = 'active' AND archived_at IS NULL "
                "AND last_seen_at < %s RETURNING id",
                (run["source_id"], run["started_at"]),
            ).fetchall()
            missing = len(rows)
        added = 0 if baseline or not successful else inserted
        return self._connection.execute(
            "UPDATE extraction_runs SET outcome = %s, finished_at = NOW(), "
            "jobs_received = %s, jobs_inserted = %s, jobs_updated = %s, "
            "jobs_added = %s, jobs_missing = %s, is_baseline = %s, "
            "complete = %s, detail = %s WHERE id = %s RETURNING *",
            (
                outcome,
                received,
                inserted,
                updated,
                added,
                missing,
                baseline,
                complete,
                detail,
                run_id,
            ),
        ).fetchone()

    def list_for_source(self, source_id: UUID) -> list[dict[str, Any]]:
        return self._connection.execute(
            "SELECT * FROM extraction_runs WHERE source_id = %s "
            "ORDER BY started_at DESC LIMIT 20",
            (source_id,),
        ).fetchall()

    def list_latest_for_all_sources(self) -> list[dict[str, Any]]:
        return self._connection.execute(
            "SELECT id, source_id, outcome, jobs_received, jobs_inserted, "
            "jobs_updated, jobs_added, jobs_missing, is_baseline, complete, "
            "detail, started_at, finished_at FROM (SELECT *, ROW_NUMBER() "
            "OVER (PARTITION BY source_id ORDER BY started_at DESC) "
            "AS source_rank FROM extraction_runs) AS ranked "
            "WHERE source_rank <= 20 ORDER BY source_id, started_at DESC"
        ).fetchall()
