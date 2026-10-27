"""Run the primary career-page investigator, then Crawlee only where it found no jobs.

Run from backend/: python diagnostics/crawl_with_fallback.py
This is a bounded diagnostic; it never calls AI or publishes vacancies.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import tempfile
import time
from datetime import datetime, timezone
from pathlib import Path

from crawlee_probe import run_probe
from investigate_careers import investigate
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def needs_fallback(primary: dict) -> bool:
    """Use Crawlee only when the primary crawler produced no job evidence."""
    return not primary.get("jobs") and not primary.get("job_count", 0)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "cape_town_tech_companies.json")
    parser.add_argument("--output", type=Path, default=ROOT / "primary_fallback_report.json")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()
    if not 1 <= args.limit <= 25:
        parser.error("--limit must be between 1 and 25")

    companies = json.loads(args.input.read_text(encoding="utf-8"))[:args.limit]
    primary_results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for company in companies:
                item = investigate(
                    browser,
                    company["name"],
                    company.get("careers_url") or company["url"],
                    max_pages=3,
                )
                primary_results.append(item)
                print(f"PRIMARY  {item['status']:<30} {item['company']}")
                time.sleep(max(0, min(args.delay, 5)))
        finally:
            browser.close()

    fallback_targets = [
        {
            "company": company["name"],
            "url": company.get("careers_url") or company["url"],
        }
        for company, result in zip(companies, primary_results)
        if needs_fallback(result)
    ]
    fallback_results = []
    if fallback_targets:
        with tempfile.TemporaryDirectory(prefix="thungatha-crawlee-") as temp_dir:
            fallback_path = Path(temp_dir) / "crawlee-fallback.json"
            asyncio.run(run_probe(fallback_targets, fallback_path, len(fallback_targets)))
            fallback_report = json.loads(fallback_path.read_text(encoding="utf-8"))
            fallback_results = fallback_report.get("results", [])

    fallback_by_company = {item["company"].casefold(): item for item in fallback_results}
    combined = []
    for primary in primary_results:
        fallback = fallback_by_company.get(primary["company"].casefold())
        combined.append({
            "company": primary["company"],
            "url": primary["start_url"],
            "primary": primary,
            "fallback_used": fallback is not None,
            "fallback": fallback,
            "outcome": (
                "primary_found_jobs" if primary.get("jobs")
                else "fallback_found_vacancy_candidates"
                if fallback and fallback.get("vacancy_candidates")
                else "unresolved_no_vacancy_evidence"
            ),
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "primary_then_fallback",
        "ai_enabled": False,
        "companies_requested": len(companies),
        "primary_jobs_found": sum(bool(item.get("jobs")) for item in primary_results),
        "fallback_attempted": len(fallback_targets),
        "fallback_candidates_found": sum(
            bool(item.get("vacancy_candidates")) for item in fallback_results
        ),
        "results": combined,
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(
        f"Report: {args.output} | primary jobs={report['primary_jobs_found']} "
        f"| fallback attempted={report['fallback_attempted']} "
        f"| fallback candidates={report['fallback_candidates_found']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
