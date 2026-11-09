from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from scout.api.vacancy_api_dependencies import get_source_preview_service
from scout.application.source_preview_service import SourcePreviewService

router = APIRouter(tags=["source previews"])


@router.post("/sources/{source_id}/preview")
async def preview_source(
    source_id: UUID,
    service: SourcePreviewService = Depends(get_source_preview_service),
) -> dict[str, Any]:
    try:
        return await service.preview_source(source_id)
    except LookupError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
