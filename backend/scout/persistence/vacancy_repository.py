from psycopg.connection import Connection

from scout.persistence.vacancy_ingestion_operations import (
    VacancyIngestionOperations,
)
from scout.persistence.vacancy_read_operations import VacancyReadOperations
from scout.persistence.vacancy_archive_operations import VacancyArchiveOperations


class VacancyRepository(
    VacancyIngestionOperations,
    VacancyReadOperations,
    VacancyArchiveOperations,
):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection
