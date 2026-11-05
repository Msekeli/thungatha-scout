import httpx

from greenhouse_adapter_test_client import retrieve_with_handler


def test_retrieves_complete_job_board_in_single_jobs_request() -> None:
    requests = []
    job = {
        "id": 1, "title": "Engineer",
        "absolute_url": "https://job-boards.greenhouse.io/demo/jobs/1",
        "content": "<p>Build software</p>",
    }

    def handler(request: httpx.Request) -> httpx.Response:
        requests.append(str(request.url))
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={"jobs": [job], "meta": {"total": 1}})
        return httpx.Response(200, json={"name": "Demo Employer"})

    result = retrieve_with_handler(handler)
    assert result.outcome == "success"
    assert result.board_name == "Demo Employer"
    assert result.jobs == [job]
    assert result.total_jobs == 1
    assert result.pages_fetched == 1
    assert result.complete is True
    assert len(requests) == 2
    assert requests[1].endswith("/jobs?content=true")


def test_reports_incomplete_inventory_when_meta_total_differs() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={
                "jobs": [{"id": 1, "title": "Engineer",
                          "absolute_url": "https://example.com/jobs/1"}],
                "meta": {"total": 2},
            })
        return httpx.Response(200, json={"name": "Demo"})

    result = retrieve_with_handler(handler)
    assert result.outcome == "partial"
    assert result.complete is False
    assert result.total_jobs == 2
    assert len(result.jobs) == 1


def test_successful_empty_board_is_distinct_from_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/jobs"):
            return httpx.Response(200, json={"jobs": [], "meta": {"total": 0}})
        return httpx.Response(200, json={"name": "Empty Employer"})

    result = retrieve_with_handler(handler, "empty")
    assert result.outcome == "empty"
    assert result.complete is True
    assert result.total_jobs == 0
