import asyncio

import httpx

from scout.ats_adapters.lever_adapter.lever_postings_client import (
    LeverPostingsClient,
)


def test_fetches_until_short_page_and_detects_duplicates() -> None:
    calls = []

    def handler(request: httpx.Request) -> httpx.Response:
        calls.append(request.url.params["skip"])
        if request.url.params["skip"] == "0":
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
    assert calls == ["0", "2"]


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
