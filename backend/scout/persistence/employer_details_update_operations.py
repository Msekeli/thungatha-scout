from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection


class EmployerDetailsUpdateOperations:
    def update_details(
        self,
        employer_id: UUID,
        values: Mapping[str, Any],
    ) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            UPDATE employers
            SET name = %s, legal_name = %s, website_url = %s,
                organization_type = %s, city = %s, province = %s,
                country = %s, updated_at = NOW()
            WHERE id = %s
            RETURNING *
            """,
            (
                values["name"],
                values.get("legal_name"),
                values.get("website_url"),
                values["organization_type"],
                values.get("city"),
                values.get("province"),
                values.get("country"),
                employer_id,
            ),
        ).fetchone()
