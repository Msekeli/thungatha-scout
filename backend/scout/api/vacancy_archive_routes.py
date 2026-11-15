from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.application.source_extraction_service import SourceExtractionService
from scout.api.vacancy_contracts import VacancyArchiveRequest

router = APIRouter()


@router.get("/vacancies/archived")
def list_archived_vacancies(
    limit: int = Query(default=200, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    service: SourceExtractionService = Depends(get_extraction_service),
) -> list[dict[str, Any]]:
    return service.list_archived_vacancies(limit, offset)


@router.post("/vacancies/{vacancy_id}/archive")
def archive_vacancy(
    vacancy_id: UUID,
    payload: VacancyArchiveRequest,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.archive_vacancy(vacancy_id, payload.reason)
    if vacancy is None:
        raise HTTPException(
            status_code=404, detail="Vacancy not found or already archived."
        )
    return vacancy


@router.post("/vacancies/{vacancy_id}/restore")
def restore_vacancy(
    vacancy_id: UUID,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    vacancy = service.restore_vacancy(vacancy_id)
    if vacancy is None:
        raise HTTPException(status_code=404, detail="Archived vacancy not found.")
    return vacancy
