import httpx

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_page_client import (
    request_teamtailor_feed_page,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_contracts import (
    TeamtailorFeedResult,
)


class TeamtailorFeedClient:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        page_size: int = 100,
        max_pages: int = 100,
    ) -> None:
        if page_size < 1 or max_pages < 1:
            raise ValueError("Teamtailor pagination limits must be positive.")
        self._client = client or httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            max_redirects=5,
            headers={"Accept": "application/rss+xml, application/xml"},
        )
        self._owns_client = client is None
        self._page_size = page_size
        self._max_pages = max_pages

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def retrieve(self, careers_url: str, feed_url: str) -> TeamtailorFeedResult:
        jobs, seen, title = [], set(), None
        for page in range(self._max_pages):
            result = await request_teamtailor_feed_page(
                self._client, careers_url, feed_url, page * self._page_size,
                self._page_size, jobs, title,
            )
            if isinstance(result, TeamtailorFeedResult):
                return result
            title = result.channel_title or title
            for job in result.jobs:
                identifier = job.get("guid")
                if isinstance(identifier, str) and identifier.strip():
                    if identifier in seen:
                        return _partial(jobs, page + 1, title, "Duplicate Teamtailor vacancy ID.")
                    seen.add(identifier)
                jobs.append(job)
            if len(result.jobs) < self._page_size:
                return TeamtailorFeedResult(
                    "success" if jobs else "empty", jobs, page + 1, True, None, title
                )
        return _partial(jobs, self._max_pages, title, "Teamtailor pagination reached its page limit.")


def _partial(jobs, pages, title, detail):
    return TeamtailorFeedResult("partial", jobs, pages, False, detail, title)
