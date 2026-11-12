import asyncio

import httpx

from scout.ats_adapters.workable_adapter.workable_source_adapter import (
    WorkableSourceAdapter,
)


def test_maps_workable_jobs_and_keeps_application_form_url() -> None:
    job = {
        "shortcode": "JOB123",
        "title": "Software Engineer",
        "url": "https://apply.workable.com/demo/j/JOB123",
        "application_url": "https://demo.workable.com/jobs/JOB123",
        "description": "<p>Build reliable software</p>",
        "city": "Cape Town",
        "country": "South Africa",
        "published_on": "2026-11-01",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"name": "Demo", "jobs": [job]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkableSourceAdapter(client).retrieve({"slug": "demo"})

    result = asyncio.run(run())
    vacancy = result.vacancies[0]
    assert result.outcome == "success"
    assert vacancy.external_job_id == "JOB123"
    assert vacancy.application_url == job["url"]
    assert vacancy.raw_payload["application_url"] == job["application_url"]
    assert vacancy.description == "Build reliable software"
    assert vacancy.location_text == "Cape Town, South Africa"


def test_malformed_job_makes_inventory_partial() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jobs": [{"title": "Missing ID"}]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkableSourceAdapter(client).retrieve({"slug": "demo"})

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert result.complete is False
    assert result.vacancies == []


def test_duplicate_ids_make_inventory_partial() -> None:
    job = {
        "shortcode": "DUPLICATE",
        "title": "Developer",
        "url": "https://apply.workable.com/demo/apply",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"jobs": [job, job]})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkableSourceAdapter(client).retrieve({"slug": "demo"})

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert len(result.vacancies) == 1
