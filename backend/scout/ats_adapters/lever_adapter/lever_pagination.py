from typing import Any

import httpx

from scout.ats_adapters.lever_adapter.lever_postings_contracts import (
    LeverPostingsResponse,
)
from scout.ats_adapters.lever_adapter.lever_response_mapper import (
    map_http_failure,
    partial_response,
)


async def retrieve_posting_pages(
    client: httpx.AsyncClient,
    endpoint: str,
    page_size: int,
    max_pages: int,
) -> LeverPostingsResponse:
    jobs: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for page_number in range(max_pages):
        page = await request_posting_page(
            client, endpoint, page_number, page_size, jobs
        )
        if isinstance(page, LeverPostingsResponse):
            return page
        for job in page:
            job_id = job.get("id")
            if not isinstance(job_id, str) or not job_id.strip() or job_id in seen_ids:
                return partial_response(
                    jobs,
                    page_number + 1,
                    "Lever returned a missing or duplicate posting ID.",
                )
            seen_ids.add(job_id)
            jobs.append(job)
        if len(page) < page_size:
            outcome = "success" if jobs else "empty"
            return LeverPostingsResponse(outcome, jobs, page_number + 1, True)
    return partial_response(
        jobs, max_pages, "Lever pagination reached the configured page limit."
    )


async def request_posting_page(
    client: httpx.AsyncClient,
    endpoint: str,
    page_number: int,
    page_size: int,
    jobs: list[dict[str, Any]],
) -> list[dict[str, Any]] | LeverPostingsResponse:
    try:
        response = await client.get(
            endpoint,
            params={
                "mode": "json",
                "skip": page_number * page_size,
                "limit": page_size,
            },
        )
    except (httpx.TimeoutException, httpx.TransportError):
        return partial_response(
            jobs,
            page_number,
            "Lever request failed or timed out.",
            "transient_failure",
        )
    failure = map_http_failure(response, jobs, page_number)
    if failure:
        return failure
    try:
        page = response.json()
    except ValueError:
        return partial_response(
            jobs, page_number, "Lever returned invalid JSON.", "malformed"
        )
    if not isinstance(page, list) or not all(isinstance(x, dict) for x in page):
        return partial_response(
            jobs,
            page_number,
            "Lever postings response must be a JSON array.",
            "malformed",
        )
    return page
