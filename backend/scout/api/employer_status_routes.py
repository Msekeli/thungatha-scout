from typing import Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from psycopg.errors import ForeignKeyViolation

from scout.api.employer_api_dependencies import get_employer_service

router = APIRouter()


class EmployerStatusUpdate(BaseModel):
    status: Literal["approved", "needs_review", "rejected", "inactive"]


@router.patch("/{employer_id}/status")
def update_employer_status(
    employer_id: UUID,
    payload: EmployerStatusUpdate,
    service: EmployerService = Depends(get_employer_service),
) -> dict:
    employer = service.update_status(employer_id, payload.status)
    if employer is None:
        raise HTTPException(status_code=404, detail="Company not found.")
    return employer


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
            detail=(
                "This company has registered sources or vacancies. "
                "Deactivate it instead of deleting its history."
            ),
        ) from exception
    if not deleted:
        raise HTTPException(status_code=404, detail="Company not found.")
