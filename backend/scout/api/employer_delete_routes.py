from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg.errors import ForeignKeyViolation

from scout.api.employer_api_dependencies import get_employer_service
from scout.application.employer_service import EmployerService

router = APIRouter()


@router.delete("/{employer_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_employer(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> None:
    try:
        deleted = service.delete_employer(employer_id)
    except ForeignKeyViolation as exception:
        raise HTTPException(
            status_code=409,
            detail="Company cannot be deleted while dependent records still exist.",
        ) from exception
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found.")
