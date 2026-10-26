"""Independent, bounded search-backend comparison."""
from app.application.discovery_config import COMPARISON_SEARCH_BACKENDS, DEFAULT_QUERIES
from app.application.discovery_runner import run_discovery
from app.application.discovery_search import DDGSSearchProvider
from app.domain.discovery import DiscoveryOutcome


def compare_search_backends(*, backends: tuple[str, ...] = COMPARISON_SEARCH_BACKENDS,
                            queries: tuple[str, ...] = DEFAULT_QUERIES,
                            max_results_per_query: int = 8,
                            region: str = "za-en") -> dict[str, object]:
    """Compare raw leads and failures without hiding backend behavior."""
    if not backends or len(set(backends)) != len(backends):
        raise ValueError("Provide one or more unique search backends")
    comparisons = []
    for backend in backends:
        report = run_discovery(provider=DDGSSearchProvider(backends=(backend,)),
                               queries=queries, max_results_per_query=max_results_per_query,
                               region=region)
        rows = report.query_reports
        comparisons.append({
            "backend": backend, "status": report.status, "query_count": len(rows),
            "successful_queries": sum(r.run.outcome != DiscoveryOutcome.REQUEST_FAILED for r in rows),
            "failed_queries": sum(r.run.outcome == DiscoveryOutcome.REQUEST_FAILED for r in rows),
            "raw_result_count": sum(r.raw_result_count for r in rows),
            "excluded_aggregator_count": sum(r.excluded_aggregator_count for r in rows),
            "discarded_result_count": sum(r.discarded_result_count for r in rows),
            "distinct_candidate_urls": len(report.candidates),
            "candidate_urls": [{"url": str(c.observed_url), "evidence": [
                {"query": e.query, "title_and_snippet": e.excerpt} for e in c.evidence
            ]} for c in report.candidates],
            "query_outcomes": [{"query": r.query, "outcome": r.run.outcome.value,
                "raw_result_count": r.raw_result_count,
                "excluded_aggregator_count": r.excluded_aggregator_count,
                "error_code": getattr(r.run, "error_code", None),
                "error_message": getattr(r.run, "error_message", None)}
                for r in rows],
        })
    return {"comparison_scope": {"region": region, "queries": list(queries),
        "max_results_per_query": max_results_per_query,
        "note": ("Counts are raw leads after known-aggregator exclusion, not verified direct "
                 "employers. Review candidate URLs and official careers-page linkage manually.")},
        "backends": comparisons}
