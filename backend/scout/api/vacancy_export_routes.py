from typing import Annotated

from fastapi import APIRouter, Depends, Query

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.api.vacancy_export_authentication import require_vacancy_export_access
from scout.api.vacancy_export_contracts import VacancyExportPage
from scout.application.greenhouse_extraction_service import GreenhouseExtractionService

router = APIRouter(
    dependencies=[Depends(require_vacancy_export_access)],
)


@router.get("/vacancies/export", response_model=VacancyExportPage)
def export_vacancies(
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
    location_scope: Annotated[
        str,
        Query(pattern="^(cape_town|western_cape|south_africa|all)$"),
    ] = "south_africa",
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict:
    return service.export_vacancies(
        limit=limit,
        offset=offset,
        location_scope=location_scope,
    )
