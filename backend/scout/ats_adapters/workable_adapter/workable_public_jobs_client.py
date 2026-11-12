import re

import httpx

from scout.ats_adapters.workable_adapter.workable_contracts import (
    WorkableJobsResponse,
)
from scout.ats_adapters.workable_adapter.workable_response_mapper import (
    map_workable_response,
)


class WorkablePublicJobsClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=True,
            max_redirects=3,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def retrieve(self, slug: str) -> WorkableJobsResponse:
        if not isinstance(slug, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
            raise ValueError("Workable source configuration requires a valid slug.")
        try:
            response = await self._client.get(
                f"https://www.workable.com/api/accounts/{slug}",
                params={"details": "true"},
            )
        except httpx.TooManyRedirects:
            return WorkableJobsResponse(
                "malformed", [], 0, False, "Workable exceeded the redirect limit."
            )
        except (httpx.TimeoutException, httpx.TransportError):
            return WorkableJobsResponse(
                "transient_failure", [], 0, False,
                "Workable request failed or timed out.",
            )
        return map_workable_response(response)
