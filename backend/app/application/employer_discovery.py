"""Public compatibility entry point for employer discovery.

Implementation is separated into focused modules, each kept below 100 lines.
"""
from app.application.discovery_candidates import candidate_from_hit as _candidate_from_hit
from app.application.discovery_cli import main
from app.application.discovery_comparison import compare_search_backends
from app.application.discovery_config import (
    COMPARISON_SEARCH_BACKENDS, DEFAULT_QUERIES, DEFAULT_SEARCH_BACKENDS,
    EXCLUDED_AGGREGATOR_DOMAINS, MAX_QUERIES, MAX_RESULTS_PER_QUERY,
    is_aggregator_result as _is_aggregator_result,
    validate_run_bounds as _validate_run_bounds,
)
from app.application.discovery_reports import DiscoveryBatchReport, DiscoveryQueryReport
from app.application.discovery_runner import run_discovery
from app.application.discovery_search import (
    DDGSSearchProvider, SearchHit, SearchProvider, SearchProviderError,
)


if __name__ == "__main__":
    main()
