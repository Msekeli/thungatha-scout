import asyncio

import httpx
import pytest

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_page_client import (
    request_teamtailor_feed_page,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_contracts import (
    TeamtailorFeedResult,
)

CAREERS_URL = "https://root.teamtailor.com/jobs"
FEED_URL = CAREERS_URL + ".rss"


@pytest.mark.parametrize(
    ("status", "outcome"),
    [
        (403, "blocked"),
        (404, "not_found"),
        (429, "rate_limited"),
        (503, "transient_failure"),
    ],
)
def test_classifies_http_failures(status: int, outcome: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await request_teamtailor_feed_page(
                client, CAREERS_URL, FEED_URL, 0, 100, [], None
            )

    result = asyncio.run(run())
    assert isinstance(result, TeamtailorFeedResult)
    assert result.outcome == outcome
    assert result.complete is False


def test_timeout_is_a_transient_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("timed out", request=request)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await request_teamtailor_feed_page(
                client, CAREERS_URL, FEED_URL, 0, 100, [], None
            )

    result = asyncio.run(run())
    assert isinstance(result, TeamtailorFeedResult)
    assert result.outcome == "transient_failure"
