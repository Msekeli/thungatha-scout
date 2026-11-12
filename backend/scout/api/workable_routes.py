from fastapi import APIRouter, HTTPException, Query

from scout.application.adapter_retrieval import retrieve_adapter_result
from scout.ats_adapters.workable_adapter.workable_source_adapter import (
    WorkableSourceAdapter,
)
from scout.ats_adapters.workable_adapter.workable_url_parser import (
    parse_workable_board_url,
)

router = APIRouter(prefix="/workable", tags=["workable"])


async def inspect_workable_board(source_url: str, company_name: str = "") -> dict:
    try:
        config, board_url = parse_workable_board_url(source_url)
    except ValueError as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception

    result = await retrieve_adapter_result(WorkableSourceAdapter(), config)
    detected_name = company_name.strip() or config["slug"].replace("-", " ").title()
    jobs = [
        {
            "id": vacancy.external_job_id,
            "title": vacancy.title,
            "absolute_url": vacancy.raw_payload.get("application_url")
            or vacancy.raw_payload.get("shortlink"),
            "location": {"name": vacancy.location_text},
            "content": vacancy.description,
        }
        for vacancy in result.vacancies[:5]
    ]
    return {
        "outcome": result.outcome,
        "board_token": config["slug"],
        "board_name": detected_name,
        "company_name": detected_name,
        "jobs": jobs,
        "pages_fetched": result.pages_fetched,
        "complete": result.complete,
        "detail": result.detail,
        "source_url": source_url,
        "careers_url": board_url,
        "board_url": board_url,
        "detected_adapter": "workable",
        "adapter_config": config,
        "total_vacancies": result.total_vacancies,
    }


@router.get("/inspect")
async def inspect_workable_source(
    url: str = Query(min_length=1, max_length=2048),
) -> dict:
    return await inspect_workable_board(url)


@router.get("/discover")
async def discover_workable_source(
    url: str = Query(min_length=1, max_length=2048),
    company_name: str = Query(default="", max_length=200),
) -> dict:
    return await inspect_workable_board(url, company_name)
