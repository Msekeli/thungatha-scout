from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field

from fastapi import APIRouter, Depends, HTTPException, Query, status

from scout.application.greenhouse_extraction_service import (
    GreenhouseExtractionService,
    SourceNotFoundError,
    UnsupportedAdapterError,
)

router = APIRouter(tags=["vacancies"])


def get_extraction_service() -> GreenhouseExtractionService:
    return GreenhouseExtractionService()


@router.get("/vacancies")
def list_vacancies(
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_vacancies(limit=limit, offset=offset)


@router.get("/employers/{employer_id}/vacancies")
def list_employer_vacancies(
    employer_id: UUID,
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_vacancies(employer_id, limit, offset)


@router.get("/sources/{source_id}/extraction-runs")
def list_source_extraction_runs(
    source_id: UUID,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    try:
        return service.list_extraction_runs(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception


@router.post(
    "/sources/{source_id}/extract",
    status_code=status.HTTP_200_OK,
)
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


class VacancyReviewUpdate(BaseModel):
    review_status: Literal["pending", "needs_verification", "verified", "rejected"]
    review_reason: str | None = Field(default=None, max_length=2000)


class VacancyArchiveRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


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


@router.post("/vacancies/{vacancy_id}/archive")
def archive_vacancy(
    vacancy_id: UUID,
    payload: VacancyArchiveRequest,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.archive_vacancy(vacancy_id, payload.reason)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Vacancy not found or already archived.")
    return vacancy


@router.post("/vacancies/{vacancy_id}/restore")
def restore_vacancy(
    vacancy_id: UUID,
    service: GreenhouseExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.restore_vacancy(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Archived vacancy not found.")
    return vacancy
