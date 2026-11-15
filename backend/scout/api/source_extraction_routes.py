from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from scout.api.vacancy_api_dependencies import get_extraction_service
from scout.application.source_extraction_service import SourceExtractionService
from scout.application.source_extraction_errors import (
    SourceNotFoundError,
    UnsupportedAdapterError,
)

router = APIRouter(tags=["source extraction"])


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


@router.post("/sources/{source_id}/extract", status_code=status.HTTP_200_OK)
async def extract_source(
    source_id: UUID,
    service: SourceExtractionService = Depends(get_extraction_service),
) -> dict[str, Any]:
    try:
        return await service.extract_source(source_id)
    except SourceNotFoundError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except UnsupportedAdapterError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
