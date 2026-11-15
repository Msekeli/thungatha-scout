from fastapi import APIRouter, HTTPException, Query

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.ats_adapters.workday_adapter.workday_source_adapter import (
    WorkdaySourceAdapter,
)
from scout.ats_adapters.workday_adapter.workday_url_parser import (
    parse_workday_board_url,
)


router = APIRouter(prefix="/workday", tags=["workday"])


async def inspect_workday_board(source_url: str, company_name: str = "") -> dict:
    try:
        config, board_url = parse_workday_board_url(source_url)
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    result = await retrieve_adapter_result(WorkdaySourceAdapter(), config)
    detected_name = company_name.strip() or config["site"].replace("_", " ").title()
    jobs = [
        {
            "id": vacancy.external_job_id,
            "title": vacancy.title,
            "absolute_url": vacancy.raw_payload["application_url"],
            "location": {"name": vacancy.location_text},
            "content": vacancy.description,
        }
        for vacancy in result.vacancies[:5]
    ]
    return {
        "outcome": result.outcome,
        "board_token": config["site"],
        "board_name": detected_name,
        "company_name": detected_name,
        "jobs": jobs,
        "pages_fetched": result.pages_fetched,
        "complete": result.complete,
        "detail": result.detail,
        "source_url": source_url,
        "careers_url": board_url,
        "board_url": board_url,
        "detected_adapter": "workday",
        "adapter_config": config,
        "total_vacancies": result.total_vacancies,
    }


@router.get("/inspect")
async def inspect_workday_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    return await inspect_workday_board(url)


@router.get("/discover")
async def discover_workday_source(
    url: str = Query(min_length=1, max_length=2048),
    company_name: str = Query(default="", max_length=200),
) -> dict:
    return await inspect_workday_board(url, company_name)
