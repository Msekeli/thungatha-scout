"""Bounded, evidence-first discovery of Cape Town employer leads.

Search results are leads only. This module does not verify employer identity,
location, official careers sources, source permissions, or current vacancies.
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from typing import Callable, Protocol
from urllib.parse import urlsplit

from pydantic import BaseModel, Field, HttpUrl, ValidationError

from app.domain.discovery import (
    DiscoveryEvidence,
    DiscoveryOutcome,
    DiscoveryRunResult,
    EmployerCandidate,
    IdentityStatus,
    OrganizationType,
    ReviewState,
    stable_candidate_id,
)

DEFAULT_QUERIES = (
    '"Cape Town" company careers page',
    '"Cape Town" companies "careers" "join our team"',
    '"Cape Town" employers official careers page',
    '"Cape Town" companies "work with us"',
    '"Cape Town" company "join us" jobs',
    '"Cape Town" company website vacancies careers',
    '"Cape Town" employers "current vacancies" official website',
    '"Cape Town" companies "life at" careers',
)
MAX_QUERIES = 20
MAX_RESULTS_PER_QUERY = 10
DEFAULT_SEARCH_BACKENDS = ("brave", "duckduckgo", "mojeek")
EXCLUDED_AGGREGATOR_DOMAINS = (
    "indeed.com",
    "careers24.com",
    "simplyhired.com",
    "jobssouthafrica.co.za",
    "jvrjobs.co.za",
    "capetownjobs.co.za",
    "jobleads.com",
)


class SearchProviderError(RuntimeError):
    """No configured search backend produced a trustworthy response."""


class SearchHit(BaseModel):
    """Untrusted search-engine result retained as candidate evidence."""

    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    snippet: str | None = Field(default=None, max_length=2000)


class SearchProvider(Protocol):
    def search(
        self, query: str, *, limit: int, region: str
    ) -> list[dict[str, object]]:
        """Return raw result mappings or raise an exception."""


class DDGSSearchProvider:
    """Free-first adapter with sequential backend fallback.

    DDGS can raise "No results found" when a backend fails, not only when a
    query genuinely has no matches. Such exceptions are treated as backend
    failures and are never silently converted to a successful-empty run.
    """

    def __init__(
        self,
        *,
        backends: tuple[str, ...] = DEFAULT_SEARCH_BACKENDS,
        timeout: float = 8.0,
        client_factory: Callable[..., object] | None = None,
    ) -> None:
        if not backends:
            raise ValueError("At least one DDGS backend must be configured")
        self.backends = backends
        self.timeout = timeout
        self.client_factory = client_factory

    def search(
        self, query: str, *, limit: int, region: str
    ) -> list[dict[str, object]]:
        client_factory = self.client_factory
        if client_factory is None:
            from ddgs import DDGS

            client_factory = DDGS

        failures: list[str] = []
        received_empty_response = False
        for backend in self.backends:
            try:
                client = client_factory(timeout=self.timeout)
                results = list(client.text(
                    query,
                    region=region,
                    safesearch="moderate",
                    max_results=limit,
                    backend=backend,
                ))
            except Exception as exc:
                failures.append(
                    f"{backend}: {type(exc).__name__}: {str(exc)[:180]}"
                )
                continue

            if results:
                return results
            received_empty_response = True

        if failures:
            details = "; ".join(failures)
            if received_empty_response:
                details = f"At least one backend returned empty; {details}"
            raise SearchProviderError(
                "No backend returned search results. Backend errors are not "
                f"treated as proof of an empty search. {details}"
            )
        return []


class DiscoveryQueryReport(BaseModel):
    query: str
    run: DiscoveryRunResult
    raw_result_count: int = 0
    discarded_result_count: int = 0
    excluded_aggregator_count: int = 0


class DiscoveryBatchReport(BaseModel):
    started_at: datetime
    finished_at: datetime
    status: str
    query_reports: list[DiscoveryQueryReport]
    candidates: list[EmployerCandidate]
    coverage_note: str = (
        "Search coverage is incomplete by design; results are leads, not verified "
        "employers or proof of Cape Town presence."
    )


def _validate_run_bounds(queries: list[str], limit: int) -> None:
    if not queries or len(queries) > MAX_QUERIES:
        raise ValueError(f"Provide between 1 and {MAX_QUERIES} queries")
    if limit < 1 or limit > MAX_RESULTS_PER_QUERY:
        raise ValueError(
            f"Results per query must be between 1 and {MAX_RESULTS_PER_QUERY}"
        )
    if any(not query.strip() or len(query) > 1000 for query in queries):
        raise ValueError("Queries must be non-empty and at most 1000 characters")
    if any("cape town" not in query.lower() for query in queries):
        raise ValueError("Every query must retain the Cape Town geographic scope")


def _is_aggregator_result(url: HttpUrl) -> bool:
    """Exclude known job aggregators from the employer-candidate queue."""
    parsed = urlsplit(str(url))
    host = (parsed.hostname or "").lower().rstrip(".")
    if any(
        host == domain or host.endswith(f".{domain}")
        for domain in EXCLUDED_AGGREGATOR_DOMAINS
    ):
        return True
    if host == "bing.com" and parsed.path.lower().startswith("/aclick"):
        return True
    if (
        host == "linkedin.com" or host.endswith(".linkedin.com")
    ) and parsed.path.lower().startswith("/jobs"):
        return True
    return False


def _candidate_from_hit(
    hit: SearchHit, query: str, observed_at: datetime
) -> EmployerCandidate:
    url = str(hit.url)
    excerpt = f"Title: {hit.title}"
    if hit.snippet:
        excerpt += f"\nSnippet: {hit.snippet}"
    evidence = DiscoveryEvidence(
        method="ddgs_public_web_search",
        query=query,
        observed_url=url,
        observed_at=observed_at,
        excerpt=excerpt[:2000],
        note=(
            "Search lead only. The result title and snippet do not verify "
            "employer identity, Cape Town presence, or source authority."
        ),
    )
    return EmployerCandidate(
        candidate_id=stable_candidate_id(url),
        display_name=None,
        observed_url=url,
        identity_status=IdentityStatus.UNRESOLVED,
        organization_type=OrganizationType.UNRESOLVED,
        review_state=ReviewState.DISCOVERED,
        evidence=[evidence],
        first_seen_at=observed_at,
        last_checked_at=observed_at,
    )


def run_discovery(
    provider: SearchProvider | None = None,
    *,
    queries: tuple[str, ...] = DEFAULT_QUERIES,
    max_results_per_query: int = 8,
    region: str = "za-en",
) -> DiscoveryBatchReport:
    """Run a bounded query plan and preserve each query's outcome."""
    query_list = list(queries)
    _validate_run_bounds(query_list, max_results_per_query)
    search_provider = provider or DDGSSearchProvider()
    started_at = datetime.now(timezone.utc)
    reports: list[DiscoveryQueryReport] = []
    candidates: dict[str, EmployerCandidate] = {}

    for query in query_list:
        query_started = datetime.now(timezone.utc)
        try:
            raw_results = search_provider.search(
                query, limit=max_results_per_query, region=region
            )
        except Exception as exc:
            finished = datetime.now(timezone.utc)
            run = DiscoveryRunResult(
                outcome=DiscoveryOutcome.REQUEST_FAILED,
                method="ddgs_public_web_search",
                query=query,
                started_at=query_started,
                finished_at=finished,
                error_code=type(exc).__name__,
                error_message=str(exc)[:1000] or "Search request failed",
            )
            reports.append(DiscoveryQueryReport(query=query, run=run))
            continue

        finished = datetime.now(timezone.utc)
        query_candidates: dict[str, EmployerCandidate] = {}
        discarded = 0
        excluded_aggregators = 0
        for raw in raw_results:
            try:
                hit = SearchHit.model_validate({
                    "title": raw.get("title"),
                    "url": raw.get("href") or raw.get("url"),
                    "snippet": raw.get("body") or raw.get("snippet"),
                })
            except (ValidationError, AttributeError, TypeError):
                discarded += 1
                continue

            if _is_aggregator_result(hit.url):
                excluded_aggregators += 1
                continue

            candidate = _candidate_from_hit(hit, query, finished)
            existing = query_candidates.get(candidate.candidate_id)
            if existing:
                existing.evidence.extend(candidate.evidence)
                continue
            query_candidates[candidate.candidate_id] = candidate

        outcome = (
            DiscoveryOutcome.SUCCESS_WITH_RESULTS
            if query_candidates
            else DiscoveryOutcome.SUCCESS_EMPTY
        )
        run = DiscoveryRunResult(
            outcome=outcome,
            method="ddgs_public_web_search",
            query=query,
            started_at=query_started,
            finished_at=finished,
            candidates=list(query_candidates.values()),
        )
        reports.append(DiscoveryQueryReport(
            query=query,
            run=run,
            raw_result_count=len(raw_results),
            discarded_result_count=discarded,
            excluded_aggregator_count=excluded_aggregators,
        ))

        for candidate in query_candidates.values():
            existing = candidates.get(candidate.candidate_id)
            if existing:
                existing.evidence.extend(candidate.evidence)
                existing.last_checked_at = finished
            else:
                candidates[candidate.candidate_id] = candidate

    finished_at = datetime.now(timezone.utc)
    failed = sum(
        report.run.outcome == DiscoveryOutcome.REQUEST_FAILED
        for report in reports
    )
    successful = len(reports) - failed
    status = (
        "discovery_failed" if successful == 0
        else "partial" if failed
        else "success_with_results" if candidates
        else "success_empty"
    )
    return DiscoveryBatchReport(
        started_at=started_at,
        finished_at=finished_at,
        status=status,
        query_reports=reports,
        candidates=list(candidates.values()),
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover Cape Town employers and official careers-page leads; results require review."
    )
    parser.add_argument(
        "--query", action="append", dest="queries",
        help="Optional query containing Cape Town; repeat to run several queries.",
    )
    parser.add_argument(
        "--max-results-per-query", type=int, default=8,
        help="Results per query (1-10; default: 8).",
    )
    args = parser.parse_args()
    report = run_discovery(
        queries=tuple(args.queries) if args.queries else DEFAULT_QUERIES,
        max_results_per_query=args.max_results_per_query,
    )
    print(json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False))
    if report.status == "discovery_failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
