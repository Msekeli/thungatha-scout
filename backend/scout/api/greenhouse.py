from dataclasses import asdict

from fastapi import APIRouter, HTTPException, Query

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
