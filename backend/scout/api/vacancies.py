from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.api.vacancy_archive_routes import router as archive_router
from scout.api.vacancy_export_routes import router as export_router
from scout.application.source_extraction_service import (
    SourceExtractionService,
    SourceNotFoundError,
    SourceNotApprovedError,
    UnsupportedAdapterError,
)

router = APIRouter(tags=["vacancies"])
router.include_router(archive_router)
router.include_router(export_router)


@router.get("/vacancies/metrics")
def get_vacancy_metrics(
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, int]:
    return service.get_dashboard_metrics()


@router.get("/vacancies")
def list_vacancies(
    employer_id: UUID | None = None,
    location_scope: str = Query(
        default="south_africa", pattern="^(cape_town|western_cape|south_africa|all)$"
    ),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    return service.list_vacancy_page(
        employer_id=employer_id,
        location_scope=location_scope,
        limit=limit,
        offset=offset,
    )


@router.get("/employers/{employer_id}/vacancies")
def list_employer_vacancies(
    employer_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: SourceExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_vacancies(employer_id, limit, offset)


@router.get("/extraction-runs")
def list_all_extraction_runs(
    service: SourceExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_all_extraction_runs()


@router.get("/sources/{source_id}/extraction-runs")
def list_source_extraction_runs(
    source_id: UUID,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    try:
        return service.list_extraction_runs(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception


from scout.api.source_preview_routes import router as preview_router

router.include_router(preview_router)


@router.post("/sources/{source_id}/extract", status_code=status.HTTP_200_OK)
async def extract_source(
    source_id: UUID,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    try:
        return await service.extract_source(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except SourceNotApprovedError as exception:
        raise HTTPException(status_code=409, detail=str(exception)) from exception
    except UnsupportedAdapterError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception


@router.get("/vacancies/{vacancy_id}")
def get_vacancy(
    vacancy_id: UUID,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.get_vacancy(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found.")
    return vacancy
