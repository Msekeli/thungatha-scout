import asyncio

import httpx
import pytest

from scout.ats_adapters.workday_adapter.workday_cxs_client import WorkdayCxsClient


CONFIG = {"host_prefix": "myhcm.wd3", "tenant": "myhcm", "site": "digioutsource"}


@pytest.mark.parametrize(
    ("status", "outcome"),
    [
        (401, "blocked"),
        (403, "blocked"),
        (404, "not_found"),
        (429, "rate_limited"),
        (503, "transient_failure"),
    ],
)
def test_classifies_listing_http_failures(status: int, outcome: str) -> None:
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(lambda request: httpx.Response(status))
        ) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == outcome
    assert result.complete is False


def test_timeout_is_a_transient_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ReadTimeout("request timed out", request=request)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    assert asyncio.run(run()).outcome == "transient_failure"


def test_malformed_json_is_not_an_empty_board() -> None:
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, content=b"invalid")
            )
        ) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "malformed"
    assert result.complete is False


def test_valid_empty_board_is_complete() -> None:
    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(
                lambda request: httpx.Response(
                    200, json={"total": 0, "jobPostings": []}
                )
            )
        ) as client:
            return await WorkdayCxsClient(client).list_jobs(CONFIG)

    result = asyncio.run(run())
    assert result.outcome == "empty"
    assert result.complete is True
