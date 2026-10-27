"""Run the primary career-page investigator, then Crawlee only where it found no jobs.

Run from backend/: PYTHONPATH=. python diagnostics/crawl_with_fallback.py
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

from diagnostics.crawlee_probe import run_probe
from diagnostics.investigate_careers import investigate
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def needs_fallback(primary: dict) -> bool:
    """Use Crawlee only when the primary crawler produced no job evidence."""
    return not primary.get("jobs") and not primary.get("job_count", 0)



def classify_outcome(primary: dict, fallback: dict | None) -> str:
    """Classify extraction results without confusing access failures with empty results."""
    if primary.get("jobs"):
        return "primary_found_jobs"
    if fallback and fallback.get("vacancy_candidates"):
        return "fallback_found_vacancy_candidates"
    if primary.get("status") in {"blocked", "load_failed", "dead_url"} or (
        fallback and fallback.get("status") == "request_failed"
    ):
        return "blocked_or_inaccessible"

    pages = primary.get("pages", [])
    evidence = [
        link
        for page in pages
        for link in page.get("link_evidence", [])
    ]
    if any(link.get("kind") == "application_email" for link in evidence) or any(
        page.get("application_emails") for page in pages
    ):
        return "email_based_recruitment"
    if (
        fallback and fallback.get("job_signal_count", 0) > 0
        or any(link.get("kind") in {"vacancy_or_careers_link", "job_description_pdf"}
               for link in evidence)
    ):
        return "vacancy_evidence_no_extractable_records"
    if primary.get("status") == "page_says_no_jobs":
        return "successful_no_vacancy_evidence"
    return "unresolved"

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
"outcome": classify_outcome(primary, fallback),
        })

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": "primary_then_fallback",
        "ai_enabled": False,
        "companies_requested": len(companies),
        "primary_jobs_found": sum(len(item.get("jobs", [])) for item in primary_results),
        "fallback_attempted": len(fallback_targets),
        "fallback_candidates_found": sum(
            len(item.get("vacancy_candidates", [])) for item in fallback_results
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
