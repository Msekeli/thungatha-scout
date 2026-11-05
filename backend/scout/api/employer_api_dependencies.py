from scout.application.employer_service import EmployerService
from scout.application.employer_source_update_service import (
    EmployerSourceUpdateService,
)


def get_employer_service() -> EmployerService:
    return EmployerService()


def get_employer_source_update_service() -> EmployerSourceUpdateService:
    return EmployerSourceUpdateService()
