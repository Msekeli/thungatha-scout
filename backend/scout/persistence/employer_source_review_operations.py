from collections.abc import Mapping
from typing import Any
from uuid import UUID


class EmployerSourceReviewOperations:
    def update_review(
        self,
        employer_id: UUID,
        source_id: UUID,
        values: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employer_sources
            SET status = %s, permission_status = %s,
                relationship_evidence = relationship_evidence || jsonb_build_array(
                    jsonb_build_object(
                        'evidence_url', %s, 'decision_reason', %s,
                        'recorded_at', NOW()
                    )
                ),
                verified_at = CASE WHEN %s = 'verified' THEN NOW()
                    WHEN %s <> 'verified' THEN NULL ELSE verified_at END,
                last_checked_at = NOW(), updated_at = NOW()
            WHERE employer_id = %s AND id = %s
            RETURNING *
            """,
            (
                values["status"],
                values["permission_status"],
                values.get("evidence_url") or None,
                values.get("reason") or None,
                values["status"],
                values["status"],
                employer_id,
                source_id,
            ),
        ).fetchone()
