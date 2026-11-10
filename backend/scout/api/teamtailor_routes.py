from urllib.parse import urlsplit

from fastapi import APIRouter, HTTPException, Query

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_parser import (
    NotTeamtailorFeedError,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_source_adapter import (
    TeamtailorSourceAdapter,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_url_parser import (
    parse_teamtailor_careers_url,
)

router = APIRouter(prefix="/teamtailor", tags=["teamtailor"])


async def inspect_teamtailor_board(source_url: str, company_name: str = "") -> dict:
    try:
        config, board_url = parse_teamtailor_careers_url(source_url)
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    adapter = TeamtailorSourceAdapter()
    try:
        result = await adapter.retrieve(config)
    except NotTeamtailorFeedError as exception:
        raise HTTPException(status_code=404, detail=str(exception)) from exception
    finally:
        await adapter.close()
    host = urlsplit(board_url).hostname or board_url
    detected_name = company_name.strip() or adapter.channel_title or host
    jobs = [
        {
            "id": vacancy.external_job_id,
            "title": vacancy.title,
            "absolute_url": vacancy.raw_payload.get("link"),
            "location": {"name": vacancy.location_text},
            "content": vacancy.description,
        }
        for vacancy in result.vacancies[:5]
    ]
    return {
        "outcome": result.outcome,
        "board_token": host,
        "board_name": detected_name,
        "company_name": detected_name,
        "jobs": jobs,
        "pages_fetched": result.pages_fetched,
        "complete": result.complete,
        "detail": result.detail,
        "source_url": source_url,
        "careers_url": board_url,
        "board_url": board_url,
        "detected_adapter": "teamtailor",
        "adapter_config": config,
        "total_vacancies": result.total_vacancies,
    }


@router.get("/inspect")
async def inspect_teamtailor_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    return await inspect_teamtailor_board(url)


@router.get("/discover")
async def discover_teamtailor_source(
    url: str = Query(min_length=1, max_length=2048),
    company_name: str = Query(default="", max_length=200),
) -> dict:
    return await inspect_teamtailor_board(url, company_name)
