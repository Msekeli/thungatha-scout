from psycopg.connection import Connection

from scout.persistence.vacancy_ingestion_operations import (
    VacancyIngestionOperations,
)
from scout.persistence.vacancy_read_operations import VacancyReadOperations
from scout.persistence.vacancy_review_operations import VacancyReviewOperations


class VacancyRepository(
    VacancyIngestionOperations,
    VacancyReadOperations,
    VacancyReviewOperations,
):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection
