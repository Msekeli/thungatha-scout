import asyncio

import httpx
import pytest

from scout.ats_adapters.greenhouse_adapter.greenhouse_source_adapter import (
    GreenhouseSourceAdapter,
)


def test_greenhouse_source_adapter_returns_normalized_vacancies() -> None:
    job = {
        "id": 11,
        "title": "Software Engineer",
        "absolute_url": "https://boards.greenhouse.io/demo/jobs/11",
        "location": {"name": "Cape Town"},
        "content": "<p>Build software</p>",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={"jobs": [job], "meta": {"total": 1}})
        return httpx.Response(200, json={"name": "Demo"})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            adapter = GreenhouseSourceAdapter(client)
            return await adapter.retrieve({"slug": "demo"})

    result = asyncio.run(run())
    assert result.outcome == "success"
    assert result.vacancies[0].external_job_id == "11"
    assert result.vacancies[0].location_text == "Cape Town"
    assert result.vacancies[0].application_url == job["absolute_url"]


def test_greenhouse_source_adapter_rejects_missing_slug() -> None:
    adapter = GreenhouseSourceAdapter()
    with pytest.raises(ValueError, match="slug"):
        asyncio.run(adapter.retrieve({}))
    asyncio.run(adapter.close())
