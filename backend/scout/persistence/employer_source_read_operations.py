from typing import Any
from uuid import UUID


class EmployerSourceReadOperations:
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

    def list_all(self) -> list[dict[str, Any]]:
        return self._connection.execute(
            "SELECT * FROM employer_sources ORDER BY employer_id, created_at, id"
        ).fetchall()
