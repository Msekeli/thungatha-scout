import asyncio

import httpx

from scout.ats_adapters.workday_adapter.workday_source_adapter import (
    WorkdaySourceAdapter,
)


CONFIG = {"host_prefix": "myhcm.wd3", "tenant": "myhcm",
          "site": "digioutsource"}


def test_maps_detail_description_and_application_destination() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(200, json={"total": 1, "jobPostings": [{
                "title": "Software Engineer", "externalPath": "/job/Cape-Town/Dev_JR1",
                "locationsText": "Cape Town", "bulletFields": ["JR1"],
            }]})
        assert request.url.path.endswith("/job/Cape-Town/Dev_JR1")
        return httpx.Response(200, json={"jobPostingInfo": {
            "jobReqId": "JR1", "title": "Software Engineer",
            "jobDescription": "<p>Build software</p>", "location": "Cape Town",
            "externalUrl": "https://apply.example.com/JR1",
        }})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdaySourceAdapter(
                __import__("scout.ats_adapters.workday_adapter.workday_cxs_client",
                           fromlist=["WorkdayCxsClient"]).WorkdayCxsClient(client)
            ).retrieve(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "success"
    assert result.complete is True
    assert result.vacancies[0].external_job_id == "JR1"
    assert result.vacancies[0].description == "Build software"
    assert result.vacancies[0].application_url == "https://apply.example.com/JR1"


def test_missing_detail_keeps_run_partial() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.method == "POST":
            return httpx.Response(200, json={"total": 1, "jobPostings": [{
                "title": "Developer", "externalPath": "/job/Dev_JR2",
            }]})
        return httpx.Response(404)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            from scout.ats_adapters.workday_adapter.workday_cxs_client import (
                WorkdayCxsClient,
            )
            return await WorkdaySourceAdapter(WorkdayCxsClient(client)).retrieve(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert result.complete is False
    assert result.vacancies == []
