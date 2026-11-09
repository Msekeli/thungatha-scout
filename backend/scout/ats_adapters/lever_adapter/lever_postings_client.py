import re

import httpx

from scout.ats_adapters.lever_adapter.lever_postings_contracts import (
    LeverPostingsResponse,
)
from scout.ats_adapters.lever_adapter.lever_response_mapper import (
    map_http_failure,
    partial_response,
)


class LeverPostingsClient:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        page_size: int = 100,
        max_pages: int = 100,
    ) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=False,
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
            response = await self._request_page(endpoint, page_number, jobs)
            if isinstance(response, LeverPostingsResponse):
                return response
            page = response
            for job in page:
                job_id = job.get("id")
                if (
                    not isinstance(job_id, str)
                    or not job_id.strip()
                    or job_id in seen_ids
                ):
                    return partial_response(
                        jobs,
                        page_number + 1,
                        "Lever returned a missing or duplicate posting ID.",
                    )
                seen_ids.add(job_id)
                jobs.append(job)
            if len(page) < self._page_size:
                outcome = "success" if jobs else "empty"
                return LeverPostingsResponse(outcome, jobs, page_number + 1, True)
        return partial_response(
            jobs,
            self._max_pages,
            "Lever pagination reached the configured page limit.",
        )

    async def _request_page(
        self, endpoint: str, page_number: int, jobs: list[dict[str, Any]]
    ) -> list[dict[str, Any]] | LeverPostingsResponse:
        try:
            response = await self._client.get(
                endpoint,
                params={
                    "mode": "json",
                    "skip": page_number * self._page_size,
                    "limit": self._page_size,
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
