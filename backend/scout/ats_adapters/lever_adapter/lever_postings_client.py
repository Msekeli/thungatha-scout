import re

import httpx

from scout.ats_adapters.lever_adapter.lever_pagination import (
    retrieve_posting_pages,
)
from scout.ats_adapters.lever_adapter.lever_postings_contracts import (
    LeverPostingsResponse,
)


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
        if not isinstance(slug, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
            raise ValueError("Lever source configuration requires a valid slug.")
        if region not in {"global", "eu"}:
            raise ValueError("Lever region must be 'global' or 'eu'.")
        host = "api.eu.lever.co" if region == "eu" else "api.lever.co"
        endpoint = f"https://{host}/v0/postings/{slug}"
        return await retrieve_posting_pages(
            self._client, endpoint, self._page_size, self._max_pages
        )
