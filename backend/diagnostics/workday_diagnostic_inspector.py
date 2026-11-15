from typing import Any
from diagnostics.workday_detail_auditor import audit_workday_details
from diagnostics.workday_diagnostic_models import TargetDiagnosticResult
from diagnostics.workday_listing_scanner import scan_workday_listing
from scout.ats_adapters.workday_adapter.workday_cxs_client import (
    WorkdayCxsClient,
)
from scout.ats_adapters.workday_adapter.workday_url_parser import (
    parse_workday_board_url,
)


async def inspect_workday_target(
    client: WorkdayCxsClient,
    target: dict[str, Any],
    sample_limit: int = 3,
) -> TargetDiagnosticResult:
    employer_id = target.get("employer_id", "unknown")
    name = target.get("name", employer_id)
    url = target.get("board_url", "")
    res = TargetDiagnosticResult(employer_id=employer_id, name=name, board_url=url)
    try:
        config, _ = parse_workday_board_url(url)
    except Exception as exc:
        res.errors.append(f"URL parsing failed: {exc}")
        return res
    res.host = f"{config['host_prefix']}.myworkdayjobs.com"
    res.tenant = config["tenant"]
    res.site = config["site"]

    scan = await scan_workday_listing(client._client, config)
    res.listing_status = scan.status_code
    res.reported_total = scan.reported_total
    res.unique_jobs_retrieved = len(scan.unique_paths)
    res.pages_fetched = scan.pages_fetched
    res.pagination_complete = scan.complete
    res.cap_reached = scan.cap_reached
    res.errors.extend(scan.errors)

    if scan.postings:
        audit = await audit_workday_details(
            client, config, scan.postings, sample_limit=sample_limit
        )
        res.detail_attempts = audit.attempts
        res.detail_successes = audit.successes
        res.detail_failures = audit.failures
        res.vacancies_normalized = audit.normalized_count
        res.field_audit = audit.field_audit
        res.samples = audit.samples
        res.errors.extend(audit.errors)
    return res
