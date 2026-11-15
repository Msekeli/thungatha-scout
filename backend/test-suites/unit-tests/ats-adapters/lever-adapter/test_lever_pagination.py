import asyncio

import httpx

from scout.ats_adapters.lever_adapter.lever_postings_client import (
    LeverPostingsClient,
)


def test_fetches_until_short_page_and_detects_duplicates() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        query = request.url.query.decode()
        calls.append(query)
        if "skip=0" in query:
            return httpx.Response(200, json=[{"id": "one"}, {"id": "two"}])
        return httpx.Response(200, json=[{"id": "three"}])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverPostingsClient(client, page_size=2).retrieve(
                "demo", "global"
            )

    result = asyncio.run(run())
    assert result.outcome == "success"
    assert result.complete is True
    assert result.pages_fetched == 2
    assert len(calls) == 2
    assert "skip=2" in calls[1]


def test_duplicate_ids_make_inventory_partial() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[{"id": "same"}, {"id": "same"}])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverPostingsClient(client, page_size=2).retrieve(
                "demo", "global"
            )

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert result.complete is False


def test_empty_board_is_a_complete_empty_result() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=[])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverPostingsClient(client).retrieve("demo", "global")

    result = asyncio.run(run())
    assert result.outcome == "empty"
    assert result.complete is True
    assert result.pages_fetched == 1


def test_rate_limit_is_not_reported_as_an_empty_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverPostingsClient(client).retrieve("demo", "global")

    result = asyncio.run(run())
    assert result.outcome == "rate_limited"
    assert result.complete is False


def test_eu_region_uses_eu_api_host() -> None:
    hosts = []

    def handler(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return httpx.Response(200, json=[])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverPostingsClient(client).retrieve("demo", "eu")

    result = asyncio.run(run())
    assert result.outcome == "empty"
    assert hosts == ["api.eu.lever.co"]
