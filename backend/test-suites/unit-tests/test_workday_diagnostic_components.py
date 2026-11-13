import asyncio
import httpx
from diagnostics.workday_detail_auditor import audit_workday_details
from diagnostics.workday_listing_scanner import scan_workday_listing
from scout.ats_adapters.workday_adapter.workday_contracts import (
    WorkdayDetailResult,
)


class FakeClient:
    async def get_detail(self, config, path):
        if path == "/job/fail":
            return WorkdayDetailResult("not_found", None, "Job not found")
        return WorkdayDetailResult(
            "success",
            {
                "jobPostingInfo": {
                    "jobReqId": "J1",
                    "title": "Role",
                    "jobDescription": "Text",
                }
            },
        )


def test_scan_workday_listing_marks_duplicate_inventory_incomplete() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            200,
            json={
                "total": 2,
                "jobPostings": [
                    {"externalPath": "/job/1"},
                    {"externalPath": "/job/1"},
                ],
            },
        )

    async def run():
        async with httpx.AsyncClient(transport=httpx.MockTransport(handler)) as c:
            return await scan_workday_listing(
                c, {"host_prefix": "a.wd1", "tenant": "a", "site": "s"}
            )

    res = asyncio.run(run())
    assert res.reported_total == 2
    assert len(res.unique_paths) == 1
    assert len(res.postings) == 1
    assert res.duplicates == 1
    assert res.complete is False


def test_audit_workday_details_handles_success_and_failure() -> None:
    postings = [{"externalPath": "/job/ok"}, {"externalPath": "/job/fail"}]
    res = asyncio.run(
        audit_workday_details(
            FakeClient(),
            {"host_prefix": "a.wd1", "site": "s"},
            postings,
            sample_limit=2,
        )
    )
    assert res.attempts == 2
    assert res.successes == 1
    assert res.failures == 1
    assert res.normalized_count == 1
    assert res.field_audit.has_title is True
    assert res.field_audit.has_description is True

