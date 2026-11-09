import asyncio

import httpx

from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter


def test_maps_posting_and_uses_html_description_fallback() -> None:
    job = {
        "id": "posting-1",
        "text": "Inside Sales Manager",
        "descriptionPlain": "",
        "description": "<p>Lead the team</p>",
        "categories": {"location": "Cape Town", "allLocations": ["Cape Town"]},
        "applyUrl": "https://jobs.lever.co/demo/posting-1/apply",
        "hostedUrl": "https://jobs.lever.co/demo/posting-1",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.params["mode"] == "json"
        assert request.url.params["limit"] == "100"
        return httpx.Response(200, json=[job])

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await LeverSourceAdapter(client).retrieve(
                {"slug": "demo", "region": "global"}
            )

    result = asyncio.run(run())
    assert result.outcome == "success"
    assert result.complete is True
    assert result.vacancies[0].description == "Lead the team"
    assert result.vacancies[0].published_at is None
    assert result.vacancies[0].source_updated_at is None


def test_rejects_missing_source_configuration() -> None:
    async def run():
        adapter = LeverSourceAdapter()
        try:
            await adapter.retrieve({"slug": "demo"})
        finally:
            await adapter.close()

    try:
        asyncio.run(run())
    except ValueError as error:
        assert "slug and region" in str(error)
    else:
        raise AssertionError("Expected invalid configuration to fail.")
