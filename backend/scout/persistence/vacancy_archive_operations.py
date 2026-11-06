from typing import Any
from uuid import UUID


class VacancyArchiveOperations:
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
