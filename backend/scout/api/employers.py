from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from scout.api.employer_api_dependencies import get_employer_service
from scout.api.employer_delete_routes import router as delete_router
from scout.api.employer_source_routes import router as source_router
from scout.application.employer_contracts import (
    EmployerBrandingUpdate,
    EmployerCreate,
    EmployerUpdate,
)
from scout.application.employer_service import EmployerService
from scout.branding.logo_discovery import (
    discover_employer_logo,
    is_usable_employer_logo_url,
)

router = APIRouter(prefix="/employers", tags=["employers"])
router.include_router(source_router)
router.include_router(delete_router)


@router.get("")
def list_employers(
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: EmployerService = Depends(get_employer_service),
) -> list[dict[str, Any]]:
    return service.list_employers(limit=limit, offset=offset)


@router.get("/sources")
def list_all_employer_sources(
    service: EmployerService = Depends(get_employer_service),
) -> list[dict[str, Any]]:
    return service.list_all_sources()


@router.post("", status_code=status.HTTP_201_CREATED)
def create_employer(
    payload: EmployerCreate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    return service.create_employer(payload)


@router.post("/{employer_id}/branding/discover")
async def discover_employer_branding(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any] | None:
    employer = service.get_employer(employer_id)
    if employer is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    if is_usable_employer_logo_url(employer.get("logo_url")):
        return employer

    sources = service.list_sources(employer_id)
    careers_url = next(
        (
            source["employer_careers_url"]
            for source in sources
            if source.get("employer_careers_url")
        ),
        None,
    )
    result = await discover_employer_logo(careers_url, employer.get("website_url"))
    if result is None:
        return employer
    logo_url, source_url = result
    updated = service.update_branding_if_unusable(employer_id, logo_url, source_url)
    return updated or service.get_employer(employer_id)


@router.get("/{employer_id}")
def get_employer(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    employer = service.get_employer(employer_id)
    if employer is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    return employer


@router.patch("/{employer_id}")
def update_employer(
    employer_id: UUID,
    payload: EmployerUpdate,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any]:
    employer = service.update_details(employer_id, payload)
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
