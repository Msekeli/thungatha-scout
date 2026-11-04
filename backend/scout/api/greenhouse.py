from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query
import httpx

from scout.career_site_discovery import discover_greenhouse
from scout.greenhouse_adapter import (
    GreenhouseAdapter,
    GreenhouseUrlError,
    parse_board_token,
)

router = APIRouter(prefix="/greenhouse", tags=["greenhouse"])


@router.get("/inspect")
async def inspect_greenhouse_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    try:
        board_token = parse_board_token(url)
    except GreenhouseUrlError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception

    adapter = GreenhouseAdapter()
    try:
        result = await adapter.retrieve(board_token)
        return asdict(result) | {"source_url": url}
    finally:
        await adapter.close()


@router.get("/discover")
async def discover_careers_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    try:
        discovery = await discover_greenhouse(url)
        adapter = GreenhouseAdapter()
        try:
            result = await adapter.retrieve(discovery["board_token"])
        finally:
            await adapter.close()
        return asdict(result) | discovery | {"source_url": discovery["board_url"]}
    except (ValueError, httpx.HTTPError) as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
