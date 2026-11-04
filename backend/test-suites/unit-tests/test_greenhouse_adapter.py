import asyncio
import json

import httpx
import pytest

from scout.greenhouse_adapter import (
    GreenhouseAdapter,
    GreenhouseUrlError,
    parse_board_token,
)


def test_parse_supported_greenhouse_board_urls() -> None:
    assert (
        parse_board_token("https://job-boards.greenhouse.io/takealotgroup")
        == "takealotgroup"
    )
    assert (
        parse_board_token(
            "https://job-boards.eu.greenhouse.io/bashdotcom/jobs/5017437101"
        )
        == "bashdotcom"
    )
    assert (
        parse_board_token("https://boards.greenhouse.io/embed/job_board?for=example")
        == "example"
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://boards.greenhouse.io/example",
        "https://boards.greenhouse.io.evil.test/example",
        "https://example.com/careers",
        "https://job-boards.greenhouse.io/",
        "https://user@job-boards.eu.greenhouse.io/example",
    ],
)
def test_reject_unsupported_board_urls(url: str) -> None:
    with pytest.raises(GreenhouseUrlError):
        parse_board_token(url)


def test_retrieves_complete_job_board_in_single_jobs_request() -> None:
    requests: list[str] = []
    job = {
        "id": 1,
        "title": "Engineer",
        "absolute_url": "https://job-boards.greenhouse.io/demo/jobs/1",
        "content": "<p>Build software</p>",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={"jobs": [job], "meta": {"total": 1}})
        return httpx.Response(200, json={"name": "Demo Employer"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("demo")
        assert result.outcome == "success"
        assert result.board_name == "Demo Employer"
        assert result.jobs == [job]
        assert result.total_jobs == 1
        assert result.pages_fetched == 1
        assert result.complete is True
        assert len(requests) == 2
        assert requests[1].endswith("/jobs?content=true")

    asyncio.run(run())


def test_reports_incomplete_inventory_when_meta_total_differs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(
                200,
                json={
                    "jobs": [
                        {
                            "id": 1,
                            "title": "Engineer",
                            "absolute_url": "https://example.com/jobs/1",
                        }
                    ],
                    "meta": {"total": 2},
                },
            )
        return httpx.Response(200, json={"name": "Demo"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("demo")
        assert result.outcome == "partial"
        assert result.complete is False
        assert result.total_jobs == 2
        assert len(result.jobs) == 1

    asyncio.run(run())


@pytest.mark.parametrize(
    ("status_code", "outcome"),
    [
        (403, "blocked"),
        (404, "not_found"),
        (429, "rate_limited"),
        (503, "transient_failure"),
    ],
)
def test_maps_http_failures(status_code: int, outcome: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("demo")
        assert result.outcome == outcome
        assert result.complete is False
        assert result.jobs == []

    asyncio.run(run())


def test_successful_empty_board_is_distinct_from_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={"jobs": [], "meta": {"total": 0}})
        return httpx.Response(200, json={"name": "Empty Employer"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("empty")
        assert result.outcome == "empty"
        assert result.complete is True
        assert result.total_jobs == 0

    asyncio.run(run())


def test_malformed_job_payload_is_not_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(
                200,
                content=json.dumps({"jobs": [{"id": "bad"}], "meta": {"total": 1}}),
            )
        return httpx.Response(200, json={"name": "Demo"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("demo")
        assert result.outcome == "malformed"
        assert result.complete is False

    asyncio.run(run())
