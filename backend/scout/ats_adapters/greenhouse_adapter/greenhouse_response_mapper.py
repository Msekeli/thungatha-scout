from typing import Any

import httpx

from .greenhouse_contracts import GreenhouseResult


class GreenhouseResponseMapper:
    @staticmethod
    def valid_job(job: Any) -> bool:
        return (
            isinstance(job, dict)
            and isinstance(job.get("id"), int)
            and isinstance(job.get("title"), str)
            and bool(job["title"].strip())
            and isinstance(job.get("absolute_url"), str)
            and job["absolute_url"].startswith(("https://", "http://"))
        )

    @staticmethod
    def failure(
        response: httpx.Response,
        token: str,
        board_name: str | None = None,
    ) -> GreenhouseResult | None:
        outcome = {
            403: "blocked",
            404: "not_found",
            429: "rate_limited",
        }.get(response.status_code)
        if response.status_code >= 500:
            outcome = "transient_failure"
        if outcome is None and response.is_success:
            return None
        if outcome is None:
            outcome = "malformed"
        return GreenhouseResult(
            outcome,
            token,
            board_name,
            [],
            0,
            False,
            f"Greenhouse returned HTTP {response.status_code}.",
        )

    @staticmethod
    def malformed(token: str, detail: str) -> GreenhouseResult:
        return GreenhouseResult("malformed", token, None, [], 0, False, detail)
