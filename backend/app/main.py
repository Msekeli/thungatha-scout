"""Command-line entry point for testing supported careers-board integrations."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from app.workday import fetch_jobs, summarize_jobs


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Thungatha Scout source adapter tools")
    commands = parser.add_subparsers(dest="command", required=True)

    workday = commands.add_parser(
        "workday", help="Fetch public vacancies from a Workday careers board"
    )
    workday.add_argument("careers_url", help="Official Workday careers URL")
    workday.add_argument("--max-jobs", type=int, default=40, help="Maximum listings to fetch (default: 40)")
    workday.add_argument("--details", action="store_true", help="Fetch each job's full detail record")
    workday.add_argument("--delay", type=float, default=0.25, help="Delay between requests in seconds (default: 0.25)")
    workday.add_argument("--output", type=Path, help="Optional path to save normalized jobs as JSON")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "workday":
        try:
            jobs = fetch_jobs(
                args.careers_url,
                max_jobs=args.max_jobs,
                include_details=args.details,
                request_delay_seconds=args.delay,
            )
        except (ValueError, RuntimeError) as exc:
            print(f"Workday fetch failed: {exc}")
            return 1

        summary = summarize_jobs(jobs)
        print(json.dumps(summary, indent=2, ensure_ascii=False))
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(
                json.dumps(jobs, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8",
            )
            print(f"Saved normalized jobs to: {args.output}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
