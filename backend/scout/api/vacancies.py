from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.api.vacancy_archive_routes import router as archive_router
from scout.api.vacancy_contracts import VacancyReviewUpdate
from scout.application.greenhouse_extraction_service import (
    GreenhouseExtractionService,
    SourceNotFoundError,
    UnsupportedAdapterError,
)

router = APIRouter(tags=["vacancies"])
router.include_router(archive_router)


@router.get("/vacancies")
def list_vacancies(
    employer_id: UUID | None = None,
    review_status: str | None = Query(default=None),
    location_scope: str = Query(default="cape_town", pattern="^(cape_town|south_africa|all)$"),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    return service.list_vacancy_page(
        employer_id=employer_id,
        review_status=review_status,
        location_scope=location_scope,
        limit=limit,
        offset=offset,
    )


@router.get("/employers/{employer_id}/vacancies")
def list_employer_vacancies(
    employer_id: UUID,
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_vacancies(employer_id, limit, offset)


@router.get("/extraction-runs")
def list_all_extraction_runs(
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_all_extraction_runs()


@router.get("/sources/{source_id}/extraction-runs")
def list_source_extraction_runs(
    source_id: UUID,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    try:
        return service.list_extraction_runs(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception


@router.post("/sources/{source_id}/extract", status_code=status.HTTP_200_OK)
async def extract_source(
    source_id: UUID,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    try:
        return await service.extract_source(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except UnsupportedAdapterError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception


@router.get("/vacancies/{vacancy_id}")
def get_vacancy(
    vacancy_id: UUID,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.get_vacancy(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found.")
    return vacancy


@router.patch("/vacancies/{vacancy_id}/review")
def update_vacancy_review(
    vacancy_id: UUID,
    payload: VacancyReviewUpdate,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.update_vacancy_review(
        vacancy_id, payload.review_status, payload.review_reason
    )
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found or archived.")
    return vacancy
