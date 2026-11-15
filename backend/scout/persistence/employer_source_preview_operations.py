from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.types.json import Jsonb


class EmployerSourcePreviewOperations:
    def update_discovery_preview(
        self, source_id: UUID, preview: Mapping[str, Any]
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employer_sources
            SET discovery_preview = %s, last_checked_at = NOW(), updated_at = NOW()
            WHERE id = %s RETURNING *
            """,
            (Jsonb(preview), source_id),
        ).fetchone()
