"""Thungatha Scout command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.discovery import DEFAULT_REGION, DEFAULT_ROLES, discover_companies
from app.exports import export_candidates_csv
from app.verification import inspect_careers_page


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover direct-employer careers sources.")
    subparsers = parser.add_subparsers(dest="command")

    discover = subparsers.add_parser("discover", help="Search the public web for employer leads.")
    discover.add_argument("--query", help="Run one custom search query instead of the default role set.")
    discover.add_argument("--region", default=DEFAULT_REGION)
    discover.add_argument("--max-results-per-query", type=int, default=8)
    discover.add_argument("--backend", default="auto", help="DDGS search backend, e.g. auto or brave,google.")

    verify = subparsers.add_parser("verify", help="Inspect one supplied careers URL.")
    verify.add_argument("url")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "verify":
        print(json.dumps(inspect_careers_page(args.url), indent=2, ensure_ascii=False))
        return

    # Default command is company discovery.
    query = args.query if args.command == "discover" else None
    region = args.region if args.command == "discover" else DEFAULT_REGION
    max_results = args.max_results_per_query if args.command == "discover" else 8
    backend = args.backend if args.command == "discover" else "auto"

    print("Thungatha Scout — company discovery")
    print(f"Region: {region}")
    print(f"Roles: {', '.join(DEFAULT_ROLES)}")
    print("Searching public web sources. Results are candidates and require verification.")
    try:
        candidates = discover_companies(
            query,
            region=region,
            max_results_per_query=max_results,
            backend=backend,
        )
    except Exception as exc:
        parser.exit(1, f"Discovery failed: {exc}\n")

    output_path = export_candidates_csv(
        [candidate.to_dict() for candidate in candidates],
        Path(__file__).resolve().parents[1] / "company_discovery_results.csv",
    )
    print(f"Unique candidate URLs: {len(candidates)}")
    print(f"CSV report: {output_path}")

    for candidate in candidates[:15]:
        print(f"- [{candidate.employer_type}] {candidate.name}")
        print(f"  {candidate.source_url}")


if __name__ == "__main__":
    main()
