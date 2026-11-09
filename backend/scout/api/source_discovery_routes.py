from fastapi import APIRouter, HTTPException, Query
import httpx

from scout.application.careers_source_discovery import discover_careers_source

router = APIRouter(prefix="/sources", tags=["source-discovery"])


@router.get("/discover")
async def discover_source(
    url: str = Query(min_length=1, max_length=2048),
    company_name: str = Query(default="", max_length=200),
) -> dict:
    try:
        return await discover_careers_source(url, company_name)
    except (ValueError, httpx.HTTPError) as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
