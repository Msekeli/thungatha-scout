import httpx
from xml.etree import ElementTree

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_contracts import (
    TeamtailorFeedResult,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_parser import (
    NotTeamtailorFeedError,
    parse_teamtailor_feed,
)


class TeamtailorFeedClient:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        page_size: int = 100,
        max_pages: int = 100,
    ) -> None:
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
            try:
                response = await self._client.get(
                    feed_url,
                    params={"offset": page * self._page_size, "per_page": self._page_size},
                )
            except (httpx.TimeoutException, httpx.TransportError):
                return _failure(jobs, page, "Teamtailor request failed or timed out.", "transient_failure", title)
            if not response.is_success:
                outcome = {401: "blocked", 403: "blocked", 404: "not_found", 429: "rate_limited"}.get(response.status_code)
                outcome = outcome or ("transient_failure" if response.status_code >= 500 else "malformed")
                return _failure(jobs, page, f"Teamtailor returned HTTP {response.status_code}.", outcome, title)
            try:
                feed = parse_teamtailor_feed(response.content, careers_url)
            except NotTeamtailorFeedError:
                raise
            except (ElementTree.ParseError, ValueError) as exception:
                return _failure(jobs, page, f"Invalid Teamtailor RSS: {exception}", "malformed", title)
            if title and feed.channel_title and title != feed.channel_title:
                return _failure(jobs, page, "Teamtailor channel title changed during pagination.", "partial", title)
            title = feed.channel_title or title
            for job in feed.jobs:
                identifier = job.get("guid")
                if isinstance(identifier, str) and identifier.strip():
                    if identifier in seen:
                        return _failure(jobs, page + 1, "Duplicate Teamtailor vacancy ID.", "partial", title)
                    seen.add(identifier)
                jobs.append(job)
            if len(feed.jobs) < self._page_size:
                return TeamtailorFeedResult(
                    "success" if jobs else "empty", jobs, page + 1, True, None, title
                )
        return _failure(jobs, self._max_pages, "Teamtailor pagination reached its page limit.", "partial", title)


def _failure(jobs, pages, detail, outcome, title):
    return TeamtailorFeedResult(
        "partial" if jobs else outcome, jobs, pages, False, detail, title
    )
