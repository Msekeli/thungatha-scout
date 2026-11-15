import asyncio

import httpx

from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_client import (
    TeamtailorFeedClient,
)

BASE = "https://root.teamtailor.com/jobs"
XML = """<rss xmlns:tt="https://teamtailor.com/locations"><channel>
<title>Root</title><link>https://root.teamtailor.com/jobs</link>{items}</channel></rss>"""


def item(identifier: str) -> str:
    return f"<item><guid>{identifier}</guid><title>Engineer</title></item>"


def test_fetches_offset_pages_until_short_final_page() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(dict(request.url.params))
        content = XML.format(
            items=item("one") + item("two")
            if "offset=0" in str(request.url)
            else item("three")
        )
        return httpx.Response(200, text=content)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await TeamtailorFeedClient(client, page_size=2).retrieve(
                BASE, BASE + ".rss"
            )

    result = asyncio.run(run())
    assert result.complete is True
    assert result.outcome == "success"
    assert result.pages_fetched == 2
    assert len(result.jobs) == 3
    assert calls[1]["offset"] == "2"


def test_failed_later_page_is_partial_not_complete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.params["offset"] == "0":
            return httpx.Response(200, text=XML.format(items=item("one") + item("two")))
        return httpx.Response(429)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await TeamtailorFeedClient(client, page_size=2).retrieve(
                BASE, BASE + ".rss"
            )

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert result.complete is False
    assert len(result.jobs) == 2


def test_empty_board_is_a_complete_empty_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=XML.format(items=""))

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await TeamtailorFeedClient(client).retrieve(BASE, BASE + ".rss")

    result = asyncio.run(run())
    assert result.outcome == "empty"
    assert result.complete is True
    assert result.jobs == []


def test_malformed_teamtailor_xml_is_not_reported_as_empty() -> None:
    malformed = '<rss xmlns:tt="https://teamtailor.com/locations"><channel>'

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text=malformed)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await TeamtailorFeedClient(client).retrieve(BASE, BASE + ".rss")

    result = asyncio.run(run())
    assert result.outcome == "malformed"
    assert result.complete is False
