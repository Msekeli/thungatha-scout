"""Execute a bounded query plan and preserve per-query outcomes."""
from datetime import datetime, timezone
from pydantic import ValidationError
from app.application.discovery_candidates import candidate_from_hit
from app.application.discovery_config import (
    DEFAULT_QUERIES, is_aggregator_result, validate_run_bounds,
)
from app.application.discovery_reports import DiscoveryBatchReport, DiscoveryQueryReport
from app.application.discovery_search import DDGSSearchProvider, SearchHit, SearchProvider
from app.domain.discovery import DiscoveryOutcome, DiscoveryRunResult


def _run_query(provider: SearchProvider, query: str, limit: int, region: str) -> DiscoveryQueryReport:
    started = datetime.now(timezone.utc)
    try:
        raw = provider.search(query, limit=limit, region=region)
    except Exception as exc:
        finished = datetime.now(timezone.utc)
        return DiscoveryQueryReport(query=query, run=DiscoveryRunResult(
            outcome=DiscoveryOutcome.REQUEST_FAILED, method="ddgs_public_web_search",
            query=query, started_at=started, finished_at=finished,
            error_code=type(exc).__name__, error_message=str(exc)[:1000] or "Search request failed",
        ))
    finished = datetime.now(timezone.utc)
    leads = {}
    discarded = excluded = 0
    for item in raw:
        try:
            hit = SearchHit.model_validate({
                "title": item.get("title"), "url": item.get("href") or item.get("url"),
                "snippet": item.get("body") or item.get("snippet"),
            })
        except (ValidationError, AttributeError, TypeError):
            discarded += 1
            continue
        if is_aggregator_result(hit.url):
            excluded += 1
            continue
        candidate = candidate_from_hit(hit, query, finished)
        existing = leads.get(candidate.candidate_id)
        if existing:
            existing.evidence.extend(candidate.evidence)
        else:
            leads[candidate.candidate_id] = candidate
    outcome = DiscoveryOutcome.SUCCESS_WITH_RESULTS if leads else DiscoveryOutcome.SUCCESS_EMPTY
    run = DiscoveryRunResult(
        outcome=outcome, method="ddgs_public_web_search", query=query,
        started_at=started, finished_at=finished, candidates=list(leads.values()),
    )
    return DiscoveryQueryReport(query=query, run=run, raw_result_count=len(raw),
                                discarded_result_count=discarded,
                                excluded_aggregator_count=excluded)


def run_discovery(provider: SearchProvider | None = None, *,
                  queries: tuple[str, ...] = DEFAULT_QUERIES,
                  max_results_per_query: int = 8, region: str = "za-en") -> DiscoveryBatchReport:
    """Run bounded searches and merge duplicate observations."""
    query_list = list(queries)
    validate_run_bounds(query_list, max_results_per_query)
    searcher = provider or DDGSSearchProvider()
    started = datetime.now(timezone.utc)
    reports = [_run_query(searcher, query, max_results_per_query, region) for query in query_list]
    candidates = {}
    for report in reports:
        for candidate in report.run.candidates:
            existing = candidates.get(candidate.candidate_id)
            if existing:
                existing.evidence.extend(candidate.evidence)
                existing.last_checked_at = report.run.finished_at
            else:
                candidates[candidate.candidate_id] = candidate
    failed = sum(r.run.outcome == DiscoveryOutcome.REQUEST_FAILED for r in reports)
    successful = len(reports) - failed
    status = ("discovery_failed" if not successful else "partial" if failed
              else "success_with_results" if candidates else "success_empty")
    return DiscoveryBatchReport(started_at=started, finished_at=datetime.now(timezone.utc),
                                status=status, query_reports=reports,
                                candidates=list(candidates.values()))
