from typing import Any

import httpx

from scout.ats_adapters.workable_adapter.workable_contracts import (
    WorkableJobsResponse,
)


def map_workable_response(response: httpx.Response) -> WorkableJobsResponse:
    failure = map_http_failure(response)
    if failure:
        return failure
    try:
        payload: Any = response.json()
    except ValueError:
        return malformed("Workable returned invalid JSON.")
    jobs = payload.get("jobs") if isinstance(payload, dict) else None
    if not isinstance(jobs, list) or not all(isinstance(job, dict) for job in jobs):
        return malformed("Workable response must contain a jobs array.")
    outcome = "success" if jobs else "empty"
    return WorkableJobsResponse(outcome, jobs, 1, True)


def map_http_failure(response: httpx.Response) -> WorkableJobsResponse | None:
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
    return WorkableJobsResponse(
        outcome or "malformed",
        [],
        1,
        False,
        f"Workable returned HTTP {response.status_code}.",
    )


def malformed(detail: str) -> WorkableJobsResponse:
    return WorkableJobsResponse("malformed", [], 1, False, detail)
