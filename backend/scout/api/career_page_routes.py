from urllib.parse import urlparse

from fastapi import APIRouter, HTTPException, Query

from scout.crawling.career_page_crawler import CareerPageCrawler
from scout.crawling.career_page_url_validation import (
    UnsafeCareerPageUrl,
    validate_public_career_url,
)

router = APIRouter(prefix="/career-pages", tags=["career-pages"])


@router.get("/discover")
async def discover_career_page(
    url: str = Query(min_length=1, max_length=2048),
    company_name: str = Query(default="", max_length=200),
) -> dict:
    try:
        safe_url = validate_public_career_url(url)
        result = await CareerPageCrawler().crawl(safe_url)
    except UnsafeCareerPageUrl as exception:
        raise HTTPException(status_code=422, detail=str(exception)) from exception
    except RuntimeError as exception:
        raise HTTPException(status_code=503, detail=str(exception)) from exception
    host = urlparse(safe_url).hostname or ""
    page = next(iter(result.observations), None)
    name = company_name.strip() or (page.page_title if page else None) or host
    jobs = [
        {
            "id": vacancy.external_job_id,
            "title": vacancy.title,
            "absolute_url": vacancy.application_url,
            "location": {"name": vacancy.location_text},
            "content": vacancy.description,
        }
        for vacancy in result.vacancies[:5]
    ]
    return {
        "outcome": "success" if result.complete else "partial",
        "board_token": host,
        "board_name": name,
        "company_name": name,
        "jobs": jobs,
        "pages_fetched": len(result.observations),
        "complete": result.complete,
        "detail": result.detail,
        "careers_url": safe_url,
        "board_url": safe_url,
        "source_url": safe_url,
        "detected_adapter": "career_page",
        "adapter_config": {"start_url": safe_url},
        "total_vacancies": len(result.vacancies),
    }
