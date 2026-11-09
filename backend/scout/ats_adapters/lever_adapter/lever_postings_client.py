from dataclasses import dataclass
import re
from typing import Any

import httpx

from scout.ats_adapters.ats_adapter_contracts import AdapterOutcome


@dataclass(frozen=True)
class LeverPostingsResponse:
    outcome: AdapterOutcome
    jobs: list[dict[str, Any]]
    pages_fetched: int
    complete: bool
    detail: str | None = None


class LeverPostingsClient:
    def __init__(
        self, client: httpx.AsyncClient | None = None,
        page_size: int = 100, max_pages: int = 100,
    ) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=30.0, follow_redirects=False,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None
        self._page_size = page_size
        self._max_pages = max_pages

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def retrieve(self, slug: str, region: str) -> LeverPostingsResponse:
        if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
            raise ValueError("Lever source configuration requires a valid slug.")
        if region not in {"global", "eu"}:
            raise ValueError("Lever region must be 'global' or 'eu'.")
        host = "api.eu.lever.co" if region == "eu" else "api.lever.co"
        endpoint = f"https://{host}/v0/postings/{slug}"
        jobs: list[dict[str, Any]] = []
        seen_ids: set[str] = set()

        for page_number in range(self._max_pages):
            skip = page_number * self._page_size
            try:
                response = await self._client.get(
                    endpoint,
                    params={"mode": "json", "skip": skip, "limit": self._page_size},
                )
            except (httpx.TimeoutException, httpx.TransportError):
                return self._failure("transient_failure", jobs, page_number,
                                     "Lever request failed or timed out.")
            failure = self._http_failure(response, jobs, page_number)
            if failure:
                return failure
            try:
                page = response.json()
            except ValueError:
                return self._failure("malformed", jobs, page_number,
                                     "Lever returned invalid JSON.")
            if not isinstance(page, list) or not all(isinstance(x, dict) for x in page):
                return self._failure("malformed", jobs, page_number,
                                     "Lever postings response must be a JSON array.")
            for job in page:
                job_id = job.get("id")
                if not isinstance(job_id, str) or not job_id.strip() or job_id in seen_ids:
                    return self._failure("partial", jobs, page_number + 1,
                                         "Lever returned a missing or duplicate posting ID.")
                seen_ids.add(job_id)
                jobs.append(job)
            if len(page) < self._page_size:
                outcome = "success" if jobs else "empty"
                return LeverPostingsResponse(outcome, jobs, page_number + 1, True)
        return self._failure("partial", jobs, self._max_pages,
                             "Lever pagination reached the configured page limit.")

    @staticmethod
    def _http_failure(response: httpx.Response, jobs: list[dict[str, Any]],
                      pages: int) -> LeverPostingsResponse | None:
        outcome = {
            401: "blocked", 403: "blocked", 404: "not_found", 429: "rate_limited",
        }.get(response.status_code)
        if response.status_code >= 500:
            outcome = "transient_failure"
        if outcome is None and response.is_success:
            return None
        return LeverPostingsClient._failure(
            outcome or "malformed", jobs, pages,
            f"Lever returned HTTP {response.status_code}.",
        )

    @staticmethod
    def _failure(outcome: AdapterOutcome, jobs: list[dict[str, Any]],
                 pages: int, detail: str) -> LeverPostingsResponse:
        return LeverPostingsResponse(outcome, jobs, pages, False, detail)
