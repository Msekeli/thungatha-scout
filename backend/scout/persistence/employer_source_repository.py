from psycopg.connection import Connection

from scout.persistence.employer_source_create_operations import (
    EmployerSourceCreateOperations,
)
from scout.persistence.employer_source_read_operations import (
    EmployerSourceReadOperations,
)


class EmployerSourceRepository(
    EmployerSourceCreateOperations, EmployerSourceReadOperations
):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection
