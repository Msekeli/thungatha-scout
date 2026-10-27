"""Probe Crawlee's adaptive crawler against official careers pages.

Run from backend/: python diagnostics/crawlee_probe.py --company Entelect --url URL
This diagnostic captures page evidence only. It does not call AI or publish jobs.
"""
from __future__ import annotations

import argparse
import asyncio
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse, urljoin

from crawlee.crawlers import AdaptivePlaywrightCrawler, AdaptivePlaywrightCrawlingContext

ROOT = Path(__file__).resolve().parents[1]
MAX_TEXT = 5000
MAX_LINKS = 100


def capture(content, url: str, company: str) -> dict:
    title = content.title.get_text(" ", strip=True)[:300] if content.title else ""
    text = re.sub(r"\\s+", " ", content.get_text(" ", strip=True))[:MAX_TEXT]
    links = []
    seen_urls = set()
    for anchor in content.select("a[href]")[:MAX_LINKS]:
        href = urljoin(url, anchor.get("href", "")).split("#", 1)[0]
        label = re.sub(r"\\s+", " ", anchor.get_text(" ", strip=True))[:180]
        if href and href not in seen_urls:
            seen_urls.add(href)
            links.append({"text": label, "href": href})

    # Explicit /position/ routes are vacancy candidates; other career links
    # remain evidence, not job records.
    vacancy_candidates = [
        link for link in links
        if re.search(r"/position/[^/]+/?$", urlparse(link["href"]).path, re.I)
        and link["text"]
        and link["text"].casefold() not in {"read more", "apply now", "learn more"}
    ]
    career_links = [
        link for link in links
        if re.search(r"career|jobs?|vacanc|position|opening|apply", link["text"] + " " + link["href"], re.I)
    ]
    return {
        "company": company,
        "url": url,
        "host": urlparse(url).netloc,
        "status": "captured" if text else "empty_page",
        "title": title,
        "text_excerpt": text,
        "links": links,
        "career_link_count": len(career_links),
        "career_links": career_links[:40],
        "vacancy_candidate_count": len(vacancy_candidates),
        "vacancy_candidates": vacancy_candidates,
        "job_signal_count": len(re.findall(
            r"\\b(vacanc(?:y|ies)|job openings|open positions|apply now|software engineer|developer)\\b",
            text, re.I,
        )),
    }

async def run_probe(targets: list[dict], output: Path, max_requests: int) -> int:
    results: list[dict] = []
    crawler = AdaptivePlaywrightCrawler.with_beautifulsoup_static_parser(
        max_requests_per_crawl=max_requests,
        max_crawl_depth=0,
        max_request_retries=1,
    )

    @crawler.router.default_handler
    async def handle(context: AdaptivePlaywrightCrawlingContext) -> None:
        target = next(
            (item for item in targets if item["url"].rstrip("/") == context.request.url.rstrip("/")),
            {"company": "unknown", "url": context.request.url},
        )
        item = capture(context.parsed_content, context.request.url, target["company"])
        item["crawler"] = "crawlee_adaptive_playwright"
        results.append(item)
        await context.push_data(item)
        context.log.info(
            f"{item['status']} {target['company']}: "
            f"{len(item['links'])} links, {item['career_link_count']} career-like links"
        )

    @crawler.failed_request_handler
    async def failed(context, error) -> None:
        target = next(
            (item for item in targets if item["url"].rstrip("/") == context.request.url.rstrip("/")),
            {"company": "unknown", "url": context.request.url},
        )
        results.append({
            "company": target["company"], "url": context.request.url,
            "crawler": "crawlee_adaptive_playwright", "status": "request_failed",
            "error": type(error).__name__,
        })

    await crawler.run([item["url"] for item in targets])
    # Deduplicate results if a retry or handler replay captures the same page.
    unique_results = {}
    for item in results:
        key = (item.get("company"), item.get("url"), item.get("status"))
        unique_results[key] = item
    results = list(unique_results.values())
    output.write_text(json.dumps({
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "crawler": "Crawlee AdaptivePlaywrightCrawler",
        "ai_enabled": False,
        "targets": len(targets),
        "results": results,
    }, indent=2), encoding="utf-8")
    print(f"Saved Crawlee evidence report: {output}")
    for item in results:
        print(f"{item['status']:<18} {item['company']:<24} "
              f"links={len(item.get('links', [])):<3} "
              f"career_links={item.get('career_link_count', 0)} "
              f"vacancy_candidates={item.get('vacancy_candidate_count', 0)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--company", action="append", help="Company name (repeat with --url)")
    parser.add_argument("--url", action="append", help="Official careers URL (repeat with --company)")
    parser.add_argument("--input", type=Path, default=ROOT / "cape_town_tech_companies.json")
    parser.add_argument("--output", type=Path, default=ROOT / "crawlee_probe_report.json")
    parser.add_argument("--max-requests", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.max_requests <= 25:
        parser.error("--max-requests must be between 1 and 25")
    if bool(args.company) != bool(args.url):
        parser.error("--company and --url must be supplied together")
    if args.company:
        if len(args.company) != len(args.url):
            parser.error("Supply the same number of --company and --url values")
        targets = [{"company": name, "url": url} for name, url in zip(args.company, args.url)]
    else:
        companies = json.loads(args.input.read_text(encoding="utf-8"))
        targets = [
            {"company": item["name"], "url": item.get("careers_url") or item["url"]}
            for item in companies[:args.max_requests]
        ]
    if not targets:
        parser.error("No URLs to crawl")
    return asyncio.run(run_probe(targets, args.output, args.max_requests))


if __name__ == "__main__":
    raise SystemExit(main())
