from typing import Any

import httpx

from scout.ats_adapters.workday_adapter.workday_contracts import (
    WorkdayDetailResult,
    WorkdayListResult,
)


def classify_http(response: httpx.Response) -> str | None:
    return {
        401: "blocked",
        403: "blocked",
        404: "not_found",
        429: "rate_limited",
    }.get(response.status_code) or (
        "transient_failure" if response.status_code >= 500 else None
    )


def map_list_response(response: httpx.Response) -> WorkdayListResult:
    failure = classify_http(response)
    if failure or not response.is_success:
        return WorkdayListResult(
            failure or "malformed",
            [],
            0,
            1,
            False,
            f"Workday listing returned HTTP {response.status_code}.",
        )
    try:
        payload: Any = response.json()
    except ValueError:
        return malformed_list("Workday listing returned invalid JSON.")
    postings = payload.get("jobPostings") if isinstance(payload, dict) else None
    total = payload.get("total") if isinstance(payload, dict) else None
    if (
        not isinstance(postings, list)
        or not all(isinstance(item, dict) for item in postings)
        or not isinstance(total, int)
        or total < 0
    ):
        return malformed_list("Workday listing schema is invalid.")
    return WorkdayListResult(
        "success" if postings else "empty", postings, total, 1, True
    )


def map_detail_response(response: httpx.Response) -> WorkdayDetailResult:
    failure = classify_http(response)
    if failure or not response.is_success:
        return WorkdayDetailResult(
            failure or "malformed",
            None,
            f"Workday detail returned HTTP {response.status_code}.",
        )
    try:
        payload: Any = response.json()
    except ValueError:
        return WorkdayDetailResult("malformed", None, "Workday detail is invalid JSON.")
    info = payload.get("jobPostingInfo") if isinstance(payload, dict) else None
    if not isinstance(info, dict):
        return WorkdayDetailResult(
            "malformed", None, "Workday detail schema is invalid."
        )
    return WorkdayDetailResult("success", payload)


def malformed_list(detail: str) -> WorkdayListResult:
    return WorkdayListResult("malformed", [], 0, 1, False, detail)
