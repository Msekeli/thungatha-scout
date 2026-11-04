from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from psycopg.errors import UniqueViolation

from scout.application.employer_contracts import (
    EmployerSourceCreate,
    EmployerSourceReviewUpdate,
)
from scout.application.employer_service import EmployerService
from scout.application.employer_source_update_service import (
    EmployerSourceUpdate,
    EmployerSourceUpdateService,
)
from scout.registry_loader import RegistryValidationError, validate_source_config

router = APIRouter()


def get_employer_service() -> EmployerService:
    return EmployerService()


def get_source_update_service() -> EmployerSourceUpdateService:
    return EmployerSourceUpdateService()



@router.get("/{employer_id}/sources")
def list_employer_sources(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> list[dict[str, Any]]:
    if service.get_employer(employer_id) is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    return service.list_sources(employer_id)


@router.post("/{employer_id}/sources", status_code=status.HTTP_201_CREATED)
def create_employer_source(
    employer_id: UUID,
    payload: EmployerSourceCreate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    if payload.employer_id != employer_id:
        raise HTTPException(
            status_code=422,
            detail="Employer ID in the path and request body must match.",
        )
    if service.get_employer(employer_id) is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    try:
        validate_source_config(payload.adapter_key, payload.adapter_config)
    except RegistryValidationError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    return service.create_source(payload)


@router.patch("/{employer_id}/sources/{source_id}/review")
def update_employer_source_review(
    employer_id: UUID,
    source_id: UUID,
    payload: EmployerSourceReviewUpdate,
    service: EmployerSourceUpdateService = Depends(get_source_update_service),
) -> dict[str, Any]:
    if payload.status == "verified" and payload.permission_status == "allowed":
        if not payload.evidence_url:
            raise HTTPException(
                status_code=422,
                detail="Evidence URL is required to verify and permit a source.",
            )
    source = service.update_review(employer_id, source_id, payload.model_dump())
    if source is None:
        raise HTTPException(status_code=404, detail="Employer source not found.")
    return source


@router.put("/{employer_id}/sources/{source_id}")
def update_employer_source(
    employer_id: UUID,
    source_id: UUID,
    payload: EmployerSourceUpdate,
    service: EmployerSourceUpdateService = Depends(get_source_update_service),
) -> dict[str, Any]:
    try:
        validate_source_config(payload.adapter_key, payload.adapter_config)
        source = service.update_configuration(employer_id, source_id, payload)
    except RegistryValidationError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    except UniqueViolation as exception:
        raise HTTPException(
            status_code=409, detail="That source URL is already registered."
        ) from exception
    if source is None:
        raise HTTPException(status_code=404, detail="Employer source not found.")
    return source
