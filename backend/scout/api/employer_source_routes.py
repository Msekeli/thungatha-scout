from typing import Any, Literal
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from psycopg.errors import ForeignKeyViolation, UniqueViolation

from scout.application.employer_contracts import EmployerSourceCreate
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


class EmployerSourceReviewUpdate(BaseModel):
    status: Literal[
        "discovered", "pending_verification", "verified",
        "temporarily_unavailable", "invalid", "needs_review", "inactive",
    ]
    permission_status: Literal["unknown", "allowed", "restricted", "needs_review"]
    evidence_url: str | None = Field(default=None, max_length=2048)
    reason: str | None = Field(default=None, max_length=2000)


class EmployerStatusUpdate(BaseModel):
    status: Literal["approved", "needs_review", "rejected", "inactive"]


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


@router.patch("/{employer_id}/status")
def update_employer_status(
    employer_id: UUID,
    payload: EmployerStatusUpdate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
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
