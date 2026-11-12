import asyncio

import httpx
import pytest

from scout.ats_adapters.workable_adapter.workable_public_jobs_client import (
    WorkablePublicJobsClient,
)


def test_requests_documented_public_endpoint_with_details() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.host == "www.workable.com"
        assert request.url.path == "/api/accounts/demo"
        assert request.url.params["details"] == "true"
        return httpx.Response(200, json={"jobs": []})

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkablePublicJobsClient(client).retrieve("demo")

    assert asyncio.run(run()).outcome == "empty"


def test_follows_public_widget_redirect() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.host == "www.workable.com":
            return httpx.Response(
                302, headers={"Location": "https://apply.workable.com/widget"}
            )
        assert request.url.host == "apply.workable.com"
        return httpx.Response(200, json={"jobs": []})

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler), follow_redirects=True
        ) as client:
            return await WorkablePublicJobsClient(client).retrieve("demo")

    assert asyncio.run(run()).outcome == "empty"


def test_rejects_invalid_slug_before_request() -> None:
    async def run():
        client = WorkablePublicJobsClient()
        try:
            await client.retrieve("../private")
        finally:
            await client.close()

    with pytest.raises(ValueError, match="valid slug"):
        asyncio.run(run())


def test_rate_limit_is_not_an_empty_board() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkablePublicJobsClient(client).retrieve("demo")

    result = asyncio.run(run())
    assert result.outcome == "rate_limited"
    assert result.complete is False


def test_transport_failure_is_reported_as_transient() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("offline", request=request)

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as client:
            return await WorkablePublicJobsClient(client).retrieve("demo")

    result = asyncio.run(run())
    assert result.outcome == "transient_failure"
    assert result.complete is False


def test_redirect_loop_is_bounded() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(302, headers={"Location": str(request.url)})

    async def run():
        async with httpx.AsyncClient(
            transport=httpx.MockTransport(handler),
            follow_redirects=True,
            max_redirects=3,
        ) as client:
            return await WorkablePublicJobsClient(client).retrieve("demo")

    result = asyncio.run(run())
    assert result.outcome == "malformed"
    assert result.complete is False
