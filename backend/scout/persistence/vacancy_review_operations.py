from typing import Any
from uuid import UUID


class VacancyReviewOperations:
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
