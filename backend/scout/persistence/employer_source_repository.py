from collections.abc import Mapping
from typing import Any
from uuid import UUID

from psycopg.connection import Connection

from scout.persistence.employer_source_create_operations import (
    EmployerSourceCreateOperations,
)
from scout.persistence.employer_source_read_operations import (
    EmployerSourceReadOperations,
)
from scout.persistence.employer_source_review_operations import (
    EmployerSourceReviewOperations,
)


class EmployerSourceRepository(
    EmployerSourceCreateOperations,
    EmployerSourceReadOperations,
    EmployerSourceReviewOperations,
):
    def __init__(self, connection: Connection) -> None:
        self._connection = connection
