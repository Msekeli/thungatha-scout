from psycopg.connection import Connection

from scout.persistence.employer_source_create_operations import EmployerSourceCreateOperations
from scout.persistence.employer_source_preview_operations import EmployerSourcePreviewOperations
from scout.persistence.employer_source_read_operations import EmployerSourceReadOperations


class EmployerSourceRepository(
    EmployerSourceCreateOperations,
    EmployerSourcePreviewOperations,
    EmployerSourceReadOperations,
):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection
