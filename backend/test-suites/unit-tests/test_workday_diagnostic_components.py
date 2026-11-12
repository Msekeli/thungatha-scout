import asyncio
import httpx
from diagnostics.workday_detail_auditor import audit_workday_details
from diagnostics.workday_diagnostic_models import (
    FieldAvailability,
    SampleVacancyAudit,
    TargetDiagnosticResult,
)
from diagnostics.workday_diagnostic_reporter import (
    format_summary_table,
    format_target_report,
)
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
def test_formats_reports_cleanly_and_does_not_claim_full_support() -> None:
    res = TargetDiagnosticResult(
        employer_id="emp1",
        name="Employer One",
        board_url="https://emp.wd3.myworkdayjobs.com/Site",
        host="emp.wd3.myworkdayjobs.com",
        tenant="emp",
        site="Site",
        listing_status=200,
        reported_total=10,
        unique_jobs_retrieved=10,
        pages_fetched=1,
        pagination_complete=True,
        detail_attempts=1,
        detail_successes=1,
        detail_failures=0,
        vacancies_normalized=1,
        field_audit=FieldAvailability(True, True, True, True, True),
        samples=[SampleVacancyAudit("J1", "Title", "Cape Town", 100, "https://url")],
    )
    report = format_target_report(res)
    assert "Employer One (`emp1`)" in report
    assert "**Unique Jobs Retrieved:** 10 (pages fetched: 1)" in report
    assert "Detail Coverage:** Sampled only" in report
    table = format_summary_table([res])
    assert "Listing complete; details sampled" in table
    assert "Supported" not in table
