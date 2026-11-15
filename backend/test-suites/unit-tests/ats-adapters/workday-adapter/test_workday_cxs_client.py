import asyncio
import json

import httpx

from scout.ats_adapters.workday_adapter.workday_cxs_client import WorkdayCxsClient


CONFIG = {"host_prefix": "myhcm.wd3", "tenant": "myhcm", "site": "digioutsource"}


def test_posts_twenty_and_paginates_until_total() -> None:
    offsets = []

    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        offsets.append(body["offset"])
        assert body["limit"] == 20
        count = 20 if body["offset"] == 0 else 1
        jobs = [
            {"externalPath": f"/job/{index}"}
            for index in range(body["offset"], body["offset"] + count)
        ]
        return httpx.Response(200, json={"total": 21, "jobPostings": jobs})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert offsets == [0, 20]
    assert result.complete is True
    assert len(result.postings) == 21


def test_reports_result_cap_as_partial() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        jobs = [
            {"externalPath": f"/job/{i}"}
            for i in range(body["offset"], body["offset"] + 20)
        ]
        return httpx.Response(200, json={"total": 2001, "jobPostings": jobs})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "partial"
    assert result.complete is False
    assert len(result.postings) == 2000


def test_rate_limit_is_not_an_empty_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "rate_limited"
    assert result.complete is False


def test_paginates_when_subsequent_pages_return_total_zero() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        body = json.loads(request.content)
        offset = body["offset"]
        count = 20 if offset == 0 else 5
        jobs = [{"externalPath": f"/job/{i}"} for i in range(offset, offset + count)]
        total = 25 if offset == 0 else 0
        return httpx.Response(200, json={"total": total, "jobPostings": jobs})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.complete is True
    assert result.total == 25
    assert len(result.postings) == 25
