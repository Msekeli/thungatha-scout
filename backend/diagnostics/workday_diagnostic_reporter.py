from diagnostics.workday_diagnostic_models import TargetDiagnosticResult


def format_target_report(r: TargetDiagnosticResult) -> str:
    lines = [
        f"### {r.name} (`{r.employer_id}`)",
        f"- **Careers URL:** {r.board_url}",
        f"- **Workday Coordinates:** host={r.host}, tenant={r.tenant}, site={r.site}",
        f"- **Listing HTTP Status:** {r.listing_status or 'N/A'}",
        f"- **Reported Total Jobs:** {r.reported_total}",
        f"- **Unique Jobs Retrieved:** {r.unique_jobs_retrieved} (pages fetched: {r.pages_fetched})",
        f"- **Detail Requests:** {r.detail_successes} successful, {r.detail_failures} unsuccessful (attempts: {r.detail_attempts})",
        f"- **Normalized Vacancies:** {r.vacancies_normalized}",
        "- **Field Availability:** "
        f"title={r.field_audit.has_title}, "
        f"description={r.field_audit.has_description}, "
        f"location={r.field_audit.has_location}, "
        f"external_id={r.field_audit.has_external_id}, "
        f"application_url={r.field_audit.has_application_url}",
        f"- **Pagination Completeness:** {'Complete' if r.pagination_complete else 'Incomplete'}"
        f"{' (Reached 2000-result cap)' if r.cap_reached else ''}",
    ]
    if r.errors:
        lines.append(f"- **Errors:** {'; '.join(r.errors)}")
    else:
        lines.append("- **Errors:** None")
    if r.samples:
        lines.append("- **Sample Normalized Vacancies:**")
        for s in r.samples:
            lines.append(
                f"  - `{s.external_job_id}`: {s.title} | {s.location_text or 'No Location'} "
                f"| {s.description_length} chars | {s.application_url}"
            )
    return "\n".join(lines)


def format_summary_table(results: list[TargetDiagnosticResult]) -> str:
    header = (
        "| Employer | Host / Cluster | Total Jobs | Unique Retrieved | Details OK/Fail | "
        "Normalized | Complete | Status |\n"
        "|---|---|---|---|---|---|---|---|"
    )
    rows = []
    for r in results:
        status = "Supported" if r.pagination_complete and r.vacancies_normalized > 0 else (
            "Partially Supported" if r.vacancies_normalized > 0 else "Failed"
        )
        if r.cap_reached and r.vacancies_normalized > 0:
            status = "Partially Supported (Capped)"
        cluster = r.host.split(".")[1] if "." in r.host else r.host
        rows.append(
            f"| {r.name} | `{cluster}` | {r.reported_total} | {r.unique_jobs_retrieved} | "
            f"{r.detail_successes}/{r.detail_failures} | {r.vacancies_normalized} | "
            f"{'Yes' if r.pagination_complete else 'No'} | {status} |"
        )
    return "\n".join([header, *rows])
