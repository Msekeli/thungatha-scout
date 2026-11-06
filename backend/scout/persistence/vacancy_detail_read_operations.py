from typing import Any
from uuid import UUID


class VacancyDetailReadOperations:
    def get_by_id(self, vacancy_id: UUID) -> dict[str, Any] | None:
        return self._connection.execute(
            """
            SELECT v.*, s.adapter_key, e.name AS employer_name,
                   e.logo_url AS employer_logo_url,
                   e.logo_source_url AS employer_logo_source_url
            FROM vacancies v
            JOIN employer_sources s ON s.id = v.source_id
            JOIN employers e ON e.id = v.employer_id
            WHERE v.id = %s
            """,
            (vacancy_id,),
        ).fetchone()
