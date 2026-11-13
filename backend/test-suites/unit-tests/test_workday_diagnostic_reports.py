from diagnostics.workday_diagnostic_models import (
    FieldAvailability,
    SampleVacancyAudit,
    TargetDiagnosticResult,
)
from diagnostics.workday_diagnostic_reporter import (
    format_summary_table,
    format_target_report,
)


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
