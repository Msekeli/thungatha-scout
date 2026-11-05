import json

import httpx
import pytest

from greenhouse_adapter_test_client import retrieve_with_handler


@pytest.mark.parametrize("status_code,outcome", [
    (403, "blocked"),
    (404, "not_found"),
    (429, "rate_limited"),
    (503, "transient_failure"),
])
def test_maps_http_failures(status_code: int, outcome: str) -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code)

    result = retrieve_with_handler(handler)
    assert result.outcome == outcome
    assert result.complete is False
    assert result.jobs == []


def test_malformed_job_payload_is_not_success() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(
                200, content=json.dumps({"jobs": [{"id": "bad"}], "meta": {"total": 1}})
            )
        return httpx.Response(200, json={"name": "Demo"})

    result = retrieve_with_handler(handler)
    assert result.outcome == "malformed"
    assert result.complete is False
