from typing import Any

from fastapi import APIRouter, Depends, Query

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.application.greenhouse_extraction_service import GreenhouseExtractionService

router = APIRouter()


@router.get("/vacancies/export")
def export_vacancies(
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    location_scope: str = Query(
        default="south_africa",
        pattern="^(cape_town|western_cape|south_africa|all)$",
    ),
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    return service.export_vacancies(
        limit=limit, offset=offset, location_scope=location_scope
    )
