from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from scout.api.employer_api_dependencies import get_employer_service
from scout.application.employer_contracts import EmployerBrandingUpdate
from scout.application.employer_service import EmployerService
from scout.employer_branding.logo_discovery import discover_employer_logo
from scout.employer_branding.logo_http import inspect_existing_logo

router = APIRouter()


@router.post("/{employer_id}/branding/discover")
async def discover_employer_branding(
    employer_id: UUID,
    service: EmployerService = Depends(get_employer_service),
) -> dict[str, Any] | None:
    employer = service.get_employer(employer_id)
    if employer is None:
        raise HTTPException(status_code=404, detail="Employer not found.")
    logo_status = await inspect_existing_logo(employer.get("logo_url"))
    if logo_status in {"valid", "unknown"}:
        return employer
    sources = service.list_sources(employer_id)
    careers_url = next(
        (
            item.get("employer_careers_url")
            for item in sources
            if item.get("employer_careers_url")
        ),
        None,
    )
    source_urls = [item.get("source_url") for item in sources if item.get("source_url")]
    result = await discover_employer_logo(
        careers_url,
        employer.get("website_url"),
        source_urls=source_urls,
        diagnostics=[],
        employer_name=employer.get("name", ""),
    )
    if result is None:
        return employer
    logo_url, source_url, logo_type = result
    updated = service.update_branding_if_unusable(
        employer_id, employer.get("logo_url"), logo_url, source_url, logo_type
    )
    return updated or service.get_employer(employer_id)


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
