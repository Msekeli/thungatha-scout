from typing import Any

import httpx

from scout.ats_adapters.lever_adapter.lever_postings_contracts import (
    LeverPostingsResponse,
)


def partial_response(
    jobs: list[dict[str, Any]],
    pages: int,
    detail: str,
    outcome: str = "partial",
) -> LeverPostingsResponse:
    return LeverPostingsResponse(outcome, jobs, pages, False, detail)


def map_http_failure(
    response: httpx.Response,
    jobs: list[dict[str, Any]],
    pages: int,
) -> LeverPostingsResponse | None:
    outcome = {
        401: "blocked",
        403: "blocked",
        404: "not_found",
        429: "rate_limited",
    }.get(response.status_code)
    if response.status_code >= 500:
        outcome = "transient_failure"
    if outcome is None and response.is_success:
        return None
    return partial_response(
        jobs,
        pages,
        f"Lever returned HTTP {response.status_code}.",
        outcome or "malformed",
    )
