from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from scout.api.employer_source_routes import router as source_router
from scout.application.employer_contracts import (
    EmployerBrandingUpdate,
    EmployerCreate,
)
from scout.application.employer_service import EmployerService

router = APIRouter(prefix="/employers", tags=["employers"])
router.include_router(source_router)


def get_employer_service() -> EmployerService:
    return EmployerService()


@router.get("")
def list_employers(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: EmployerService = Depends(get_employer_service),
) -> list[dict[str, Any]]:
    return service.list_employers(limit=limit, offset=offset)


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employer(
    payload: EmployerCreate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    return service.create_employer(payload)


@router.get("/{employer_id}")
def get_employer(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    employer = service.get_employer(employer_id)
    if employer is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    return employer


@router.patch("/{employer_id}/branding")
def update_employer_branding(
    employer_id: UUID,
    payload: EmployerBrandingUpdate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    employer = service.update_branding(employer_id, payload)
    if employer is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    return employer
