from fastapi import APIRouter, HTTPException, Query

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter
from scout.ats_adapters.lever_adapter.lever_url_parser import parse_lever_board_url

router = APIRouter(prefix="/lever", tags=["lever"])


async def inspect_lever_board(source_url: str) -> dict:
    try:
        config, board_url = parse_lever_board_url(source_url)
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception

    adapter = LeverSourceAdapter()
    result = await retrieve_adapter_result(adapter, config)
    jobs = [
        {
            "id": vacancy.external_job_id,
            "title": vacancy.title,
            "absolute_url": vacancy.raw_payload.get("hostedUrl"),
            "location": {"name": vacancy.location_text},
            "content": vacancy.description,
        }
        for vacancy in result.vacancies[:5]
    ]
    return {
        "outcome": result.outcome,
        "board_token": config["slug"],
        "board_name": None,
        "jobs": jobs,
        "pages_fetched": result.pages_fetched,
        "complete": result.complete,
        "detail": result.detail,
        "source_url": source_url,
        "careers_url": source_url,
        "board_url": board_url,
        "detected_adapter": "lever",
        "adapter_config": config,
        "total_vacancies": result.total_vacancies,
        "company_name": "",
    }


@router.get("/inspect")
async def inspect_lever_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    return await inspect_lever_board(url)


@router.get("/discover")
async def discover_lever_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    result = await inspect_lever_board(url)
    return {
        key: result[key]
        for key in (
            "source_url", "careers_url", "board_url", "board_token", "board_name",
            "detected_adapter", "adapter_config", "company_name",
        )
    }
