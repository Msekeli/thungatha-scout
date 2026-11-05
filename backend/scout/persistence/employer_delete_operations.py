from uuid import UUID

from psycopg.connection import Connection


class EmployerDeleteOperations:
    def __init__(self, connection: Connection) -> None:
        self._connection = connection

    def delete(self, employer_id: UUID) -> bool:
        self._connection.execute(
            """
            DELETE FROM extraction_runs
            WHERE source_id IN (
                SELECT id FROM employer_sources WHERE employer_id = %s
            )
            """,
            (employer_id,),
        )
        self._connection.execute(
            "DELETE FROM vacancies WHERE employer_id = %s",
            (employer_id,),
        )
        self._connection.execute(
            "DELETE FROM employer_sources WHERE employer_id = %s",
            (employer_id,),
        )
        cursor = self._connection.execute(
            "DELETE FROM employers WHERE id = %s",
            (employer_id,),
        )
        return cursor.rowcount > 0
