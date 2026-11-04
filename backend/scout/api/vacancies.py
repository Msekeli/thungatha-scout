from typing import Any
from uuid import UUID

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
