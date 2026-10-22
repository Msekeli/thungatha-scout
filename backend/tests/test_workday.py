import json

import httpx
import pytest

from app.workday import (
    PAGE_SIZE,
    WorkdayError,
    fetch_jobs,
    normalize_job,
    parse_board_url,
)


def test_parse_workday_url_with_locale_and_query():
    board = parse_board_url(
        "https://myhcm.wd3.myworkdayjobs.com/en-US/Betway_Africa?utm_source=test"
    )
    assert board.tenant == "myhcm"
    assert board.site == "Betway_Africa"
    assert board.locale == "en-US"
    assert board.jobs_endpoint == (
        "https://myhcm.wd3.myworkdayjobs.com/wday/cxs/myhcm/Betway_Africa/jobs"
    )


def test_parse_workday_url_without_locale():
    board = parse_board_url("https://example.wd5.myworkdayjobs.com/External")
    assert board.site == "External"
    assert board.locale is None


@pytest.mark.parametrize("url", [
    "https://example.com/careers",
    "https://example.wd5.myworkdayjobs.com/",
    "not a URL",
])
def test_rejects_invalid_board_urls(url):
    with pytest.raises(ValueError):
        parse_board_url(url)


def test_fetch_jobs_paginates_at_twenty_and_normalizes_records():
    seen_offsets = []

    def handler(request):
        if request.method == "POST":
            body = json.loads(request.content)
            seen_offsets.append(body["offset"])
            assert body["limit"] == PAGE_SIZE == 20
            if body["offset"] == 0:
                return httpx.Response(200, json={
                    "total": 21,
                    "jobPostings": [
                        {"title": f"Role {i}", "externalPath": f"/job/role_{i}",
                         "locationsText": "Cape Town", "postedOn": "Posted Today"}
                        for i in range(20)
                    ],
                })
            return httpx.Response(200, json={
                "total": 0,
                "jobPostings": [
                    {"title": "Role 20", "externalPath": "/job/role_20",
                     "locationsText": "Remote", "postedOn": "Posted Yesterday"}
                ],
            })
        return httpx.Response(404)

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        jobs = fetch_jobs(
            "https://myhcm.wd3.myworkdayjobs.com/Betway_Africa",
            max_jobs=25,
            request_delay_seconds=0,
            client=client,
        )
    finally:
        client.close()

    assert seen_offsets == [0, 20]
    assert len(jobs) == 21
    assert jobs[0]["source_type"] == "workday"
    assert jobs[0]["title"] == "Role 0"
    assert jobs[0]["location"] == "Cape Town"
    assert jobs[0]["posted_label"] == "Posted Today"


def test_detail_fields_override_list_fields_and_build_apply_url():
    board = parse_board_url(
        "https://myhcm.wd3.myworkdayjobs.com/en-US/Betway_Africa"
    )
    job = normalize_job(
        board,
        {"title": "Short title", "externalPath": "/job/Cape-Town/Engineer_JR123",
         "locationsText": "2 Locations", "bulletFields": ["JR123"]},
        {"title": "Full title", "location": "Cape Town, South Africa",
         "jobReqId": "JR123", "startDate": "2026-10-01",
         "timeType": "Full time", "jobDescription": "<p>Build things</p>"},
    )
    assert job["title"] == "Full title"
    assert job["location"] == "Cape Town, South Africa"
    assert job["source_id"] == "JR123"
    assert job["posted_at"] == "2026-10-01"
    assert job["employment_type"] == "Full time"
    assert job["url"] == (
        "https://myhcm.wd3.myworkdayjobs.com/en-US/Betway_Africa/job/Cape-Town/Engineer_JR123"
    )


@pytest.mark.parametrize("status", [403, 429])
def test_restricted_board_is_not_misreported_as_empty(status):
    def handler(request):
        return httpx.Response(status, text="restricted")

    client = httpx.Client(transport=httpx.MockTransport(handler))
    try:
        with pytest.raises(WorkdayError, match="zero jobs"):
            fetch_jobs(
                "https://myhcm.wd3.myworkdayjobs.com/Betway_Africa",
                request_delay_seconds=0,
                client=client,
            )
    finally:
        client.close()


def test_rejects_unsafe_external_path():
    board = parse_board_url("https://myhcm.wd3.myworkdayjobs.com/Betway_Africa")
    from app.workday import fetch_job_detail

    client = httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={})))
    try:
        with pytest.raises(WorkdayError, match="unsafe externalPath"):
            fetch_job_detail(client, board, "//attacker.example/path")
    finally:
        client.close()
