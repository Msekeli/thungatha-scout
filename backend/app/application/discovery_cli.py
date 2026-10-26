"""Command-line entry point for discovery and backend comparison."""
import argparse
import json
from app.application.discovery_comparison import compare_search_backends
from app.application.discovery_config import COMPARISON_SEARCH_BACKENDS, DEFAULT_QUERIES
from app.application.discovery_runner import run_discovery


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Discover Cape Town employers and official careers-page leads; results require review.")
    parser.add_argument("--query", action="append", dest="queries",
                        help="Optional query containing Cape Town; repeat for several queries.")
    parser.add_argument("--max-results-per-query", type=int, default=8,
                        help="Results per query (1-10; default: 8).")
    parser.add_argument("--compare-backends", action="store_true",
                        help="Compare Bing, Brave, DuckDuckGo and Mojeek independently.")
    parser.add_argument("--backends", default=",".join(COMPARISON_SEARCH_BACKENDS),
                        help="Comma-separated backend names for --compare-backends.")
    args = parser.parse_args()
    queries = tuple(args.queries) if args.queries else DEFAULT_QUERIES
    if args.compare_backends:
        report = compare_search_backends(
            backends=tuple(x.strip() for x in args.backends.split(",") if x.strip()),
            queries=queries, max_results_per_query=args.max_results_per_query)
        print(json.dumps(report, indent=2, ensure_ascii=False))
        if all(x["failed_queries"] == x["query_count"] for x in report["backends"]):
            raise SystemExit(1)
        return
    report = run_discovery(queries=queries, max_results_per_query=args.max_results_per_query)
    print(json.dumps(report.model_dump(mode="json"), indent=2, ensure_ascii=False))
    if report.status == "discovery_failed":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
