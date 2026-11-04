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
    assert parse_board_token("https://job-boards.greenhouse.io/takealotgroup") == (
        "takealotgroup"
    )
    assert parse_board_token(
        "https://boards.greenhouse.io/embed/job_board?for=example"
    ) == "example"


@pytest.mark.parametrize(
    "url",
    [
        "http://boards.greenhouse.io/example",
        "https://boards.greenhouse.io.evil.test/example",
        "https://example.com/careers",
        "https://job-boards.greenhouse.io/",
    ],
)
def test_reject_unsupported_board_urls(url: str) -> None:
    with pytest.raises(GreenhouseUrlError):
        parse_board_token(url)


def test_retrieves_jobs_and_follows_next_link() -> None:
    requests: list[str] = []

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.params.get("page") == "2":
            return httpx.Response(200, json={"jobs": []})
        if request.url.path.endswith("/jobs"):
            return httpx.Response(
                200,
                json={
                    "jobs": [
                        {
                            "id": 1,
                            "title": "Engineer",
                            "absolute_url": "https://example.com/job/1",
                        }
                    ]
                },
                headers={
                    "Link": (
                        '<https://boards-api.greenhouse.io/v1/boards/demo/jobs'
                        '?content=true&page=2>; rel="next"'
                    )
                },
            )
        return httpx.Response(200, json={"name": "Demo Employer"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            adapter = GreenhouseAdapter(client)
            result = await adapter.retrieve("demo")

        assert result.outcome == "success"
        assert result.board_name == "Demo Employer"
        assert len(result.jobs) == 1
        assert result.pages_fetched == 2
        assert result.complete is True
        assert len(requests) == 3

    asyncio.run(run())


@pytest.mark.parametrize(
    ("status_code", "outcome"),
    [\n        (403, "blocked"),\n        (404, "not_found"),\n        (429, "rate_limited"),\n        (503, "transient_failure"),\n    ],
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

    asyncio.run(run())


def test_malformed_job_payload_is_not_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, content=json.dumps({"jobs": [{"id": "bad"}]}))
        return httpx.Response(200, json={"name": "Demo"})

    async def run() -> None:
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            result = await GreenhouseAdapter(client).retrieve("demo")
        assert result.outcome == "malformed"
        assert result.complete is False

    asyncio.run(run())
