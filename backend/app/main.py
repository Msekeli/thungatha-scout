"""Thungatha Scout command-line entry point."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.discovery import DEFAULT_REGION, DEFAULT_ROLES, discover_companies
from app.exports import export_candidates_csv
from app.greenhouse_discovery import discover_greenhouse_boards, save_greenhouse_discovery_report
from app.greenhouse_analysis import analyze_greenhouse_report
from app.verification import inspect_careers_page
from app.site_investigator import investigate_careers_url, save_investigation_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Discover direct-employer careers sources.")
    subparsers = parser.add_subparsers(dest="command")

    discover = subparsers.add_parser("discover", help="Search the public web for employer leads.")
    discover.add_argument("--query", help="Run one custom search query instead of the default role set.")
    discover.add_argument("--region", default=DEFAULT_REGION)
    discover.add_argument("--max-results-per-query", type=int, default=8)
    discover.add_argument("--backend", default="auto", help="DDGS search backend, e.g. auto or brave,google.")

    greenhouse = subparsers.add_parser(
        "discover-greenhouse",
        help="Automatically find public Greenhouse boards and validate their job feeds.",
    )
    greenhouse.add_argument("--max-results-per-query", type=int, default=20)
    greenhouse.add_argument("--backend", default="brave,google", help="Comma-separated DDGS search backends, e.g. brave,google.")
    greenhouse.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "reports" / "greenhouse-discovery"),
        help="Directory for timestamped JSON evidence and CSV board registry.",
    )

    analyze_greenhouse = subparsers.add_parser(
        "analyze-greenhouse",
        help="Rank saved Greenhouse vacancies by South African location and software-role relevance.",
    )
    analyze_greenhouse.add_argument("report", help="Path to a saved greenhouse-discovery JSON report.")
    analyze_greenhouse.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "reports" / "greenhouse-analysis"),
        help="Directory for ranked JSON and CSV reports.",
    )

    verify = subparsers.add_parser("verify", help="Run the original lightweight URL check.")
    verify.add_argument("url")

    investigate = subparsers.add_parser(
        "investigate",
        help="Investigate one supplied careers URL and try supported public ATS endpoints.",
    )
    investigate.add_argument("url")
    investigate.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parents[1] / "reports" / "url-investigations"),
        help="Directory for separate JSON and Markdown reports.",
    )

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "discover-greenhouse":
        try:
            report = discover_greenhouse_boards(
                max_results_per_query=args.max_results_per_query,
                backend=args.backend,
            )
        except Exception as exc:
            parser.exit(1, f"Greenhouse discovery failed: {exc}\\n")
        json_path, csv_path = save_greenhouse_discovery_report(report, args.output_dir)
        print(json.dumps({
            "candidate_boards_found": report["candidate_boards_found"],
            "validated_boards_found": report["validated_boards_found"],
            "boards_with_explicit_regional_jobs": report.get("boards_with_explicit_regional_jobs", 0),
            "boards_needing_company_identity_review": report.get("boards_needing_company_identity_review", 0),
            "successful_queries": report["successful_queries"],
            "failed_queries": report["failed_queries"],
            "search_result_pages_seen": report.get("search_result_pages_seen", 0),
            "company_pages_inspected": report.get("company_pages_inspected", 0),
            "company_page_errors": len(report.get("company_page_errors", [])),
            "json_report": str(json_path),
            "csv_registry": str(csv_path),
        }, indent=2, ensure_ascii=False))
        print("\nBoards with explicit Cape Town / Western Cape / Stellenbosch job evidence:")
        for board in report["boards"]:
            if board["valid"] and board.get("regional_evidence_status") == "explicit_regional_job":
                regions = ", ".join(board.get("regional_locations", []))
                print(
                    f"- {board['board_token']}: {board['regional_job_count']} regional jobs "
                    f"[{regions}] ({board['board_url']})"
                )
        print("\nAll validated boards are retained in the CSV, including boards without explicit regional jobs.")
        return

    if args.command == "analyze-greenhouse":
        try:
            summary = analyze_greenhouse_report(args.report, args.output_dir)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            parser.exit(1, f"Greenhouse report analysis failed: {exc}\\n")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        return

    if args.command == "verify":
        print(json.dumps(inspect_careers_page(args.url), indent=2, ensure_ascii=False))
        return

    if args.command == "investigate":
        report = investigate_careers_url(args.url)
        json_path, markdown_path = save_investigation_report(report, args.output_dir)
        print(json.dumps({
            "supplied_url": report.get("supplied_url"),
            "http_status": report.get("http_status"),
            "final_url": report.get("final_url"),
            "page_title": report.get("page_title"),
            "ats_detected": report.get("ats_detected"),
            "extraction_success": report.get("job_extraction", {}).get("success"),
            "jobs_extracted": len(report.get("job_extraction", {}).get("jobs", [])),
            "json_report": str(json_path),
            "markdown_report": str(markdown_path),
            "errors": report.get("errors", []),
        }, indent=2, ensure_ascii=False))
        return

    # Default command is company discovery.
    query = args.query if args.command == "discover" else None
    region = args.region if args.command == "discover" else DEFAULT_REGION
    max_results = args.max_results_per_query if args.command == "discover" else 8
    backend = args.backend if args.command == "discover" else "auto"

    print("Thungatha Scout — company discovery")
    print(f"Region: {region}")
    print("Industry filter: none (all employers are in scope)")
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
