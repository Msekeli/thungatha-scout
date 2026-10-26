"""Scan employer careers pages with a real browser and save extracted vacancies locally."""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit

from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
DEFAULT_INPUT = ROOT / "cape_town_tech_companies.json"
DEFAULT_OUTPUT = ROOT / "career_page_scan_results.json"
JOB_WORDS = re.compile(
    r"job|career|vacanc|position|opening|requisition|opportunit|apply|workday|"
    r"greenhouse|lever\.co|ashby|workable|breezy|/go/|/job[s]?/",
    re.IGNORECASE,
)
GENERIC_LINKS = {
    "home", "about", "contact", "careers", "career", "learn more", "read more",
    "view all", "view jobs", "search", "login", "sign in", "privacy", "next",
    "previous", "menu", "apply now",
}
NO_JOBS_PHRASES = (
    "no jobs found", "no jobs available", "no current vacancies",
    "no open positions", "no openings at this time", "there are currently no jobs",
    "there are no vacancies",
)
DESCRIPTION_SELECTORS = (
    "[class*='job-description']", "[class*='jobDescription']",
    "[id*='job-description']", "[class*='job-detail']",
    "[class*='jobDetail']", "article", "main", "[role='main']",
)


def read_companies(path: Path) -> list[dict[str, str]]:
    """Load and validate the simple name/URL input file."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array of company objects.")
    companies = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict) or not item.get("name") or not item.get("url"):
            raise ValueError(f"Company entry {index} must include name and url.")
        parts = urlsplit(item["url"])
        if parts.scheme not in {"http", "https"} or not parts.netloc:
            raise ValueError(f"Company entry {index} has an invalid HTTP(S) URL.")
        companies.append({"name": str(item["name"]).strip(), "url": item["url"].strip()})
    return companies


def _clean_url(url: str) -> str:
    return urldefrag(url.strip())[0].rstrip("/")


def _is_job_link(item: dict[str, str], source_url: str) -> bool:
    text = re.sub(r"\s+", " ", item.get("text", "")).strip()
    href = item.get("href", "")
    card = item.get("card_text", "")
    if not text or text.lower() in GENERIC_LINKS or len(text) > 180:
        return False
    if not href.startswith(("http://", "https://")):
        return False
    if _clean_url(href) == _clean_url(source_url):
        return False
    if any(href.lower().startswith(f"{scheme}:") for scheme in ("mailto", "tel", "javascript")):
        return False
    score = int(bool(JOB_WORDS.search(href)))
    score += int(bool(JOB_WORDS.search(text)))
    score += int(bool(re.search(r"\b(remote|hybrid|onsite|full[- ]time|permanent)\b", card, re.I)))
    score += int(bool(re.search(r"\b(apply|view job|job details|read more)\b", text, re.I)))
    return score >= 1 and not re.search(r"\b(cookie policy|privacy policy|terms of use)\b", text, re.I)


def _page_links(page: Page) -> list[dict[str, str]]:
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]')).map(a => {
          const card = a.closest(
            'article, li, [class*="job"], [class*="position"], ' +
            '[class*="vacan"], [class*="opening"], [class*="listing"]'
          );
          return {
            text: (a.innerText || a.getAttribute('aria-label') || a.title || '').trim(),
            href: a.href,
            card_text: (card ? card.innerText : a.parentElement?.innerText || '').trim()
              .slice(0, 1200)
          };
        })"""
    )


def _page_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=4000).strip()
    except Exception:
        return ""


def _job_details(page: Page, url: str, listing_text: str) -> dict[str, str]:
    page.goto(url, wait_until="domcontentloaded", timeout=30000)
    try:
        page.wait_for_load_state("networkidle", timeout=5000)
    except PlaywrightTimeoutError:
        pass
    page.wait_for_timeout(500)
    title = page.title().strip()
    text = ""
    for selector in DESCRIPTION_SELECTORS:
        try:
            candidate = page.locator(selector).first.inner_text(timeout=1200).strip()
            if len(candidate) > len(text):
                text = candidate
        except Exception:
            continue
    body = _page_text(page)
    if len(body) > len(text):
        text = body
    location = ""
    for selector in (
        "[class*='location']", "[data-automation-id*='location']",
        "[data-testid*='location']", "[aria-label*='location' i]",
    ):
        try:
            candidate = page.locator(selector).first.inner_text(timeout=800).strip()
            if candidate and len(candidate) < 180:
                location = candidate
                break
        except Exception:
            continue
    if not location:
        for line in text.splitlines():
            line = re.sub(r"\s+", " ", line).strip()
            if line and len(line) < 120 and re.search(
                r"\b(cape town|south africa|remote|hybrid|johannesburg|durban|pretoria|
                r"london|new york|san francisco|global|multiple locations)\b",
                line, re.I,
            ):
                location = line
                break
    apply_url = ""
    apply_text = ""
    for link in _page_links(page):
        label = link.get("text", "")
        href = link.get("href", "")
        if href.startswith(("http://", "https://")) and re.search(
            r"apply|submit application|apply now", label, re.I
        ):
            apply_url, apply_text = href, label
            break
    return {
        "title": title or listing_text,
        "job_url": url,
        "application_url": apply_url or url,
        "application_link_text": apply_text,
        "description": text[:30000],
        "description_truncated": len(text) > 30000,
        "location": location,
    }


def _pagination_urls(page: Page, current_url: str) -> list[str]:
    links = _page_links(page)
    found = []
    for item in links:
        label = item.get("text", "").strip().lower()
        href = item.get("href", "")
        if not href.startswith(("http://", "https://")) or _clean_url(href) == _clean_url(current_url):
            continue
        if re.search(r"\b(next|older|more jobs)\b|[?&](page|offset|start)=|/page/\d+", label + " " + href, re.I):
            found.append(href)
    return list(dict.fromkeys(found))


def scan_company(
    browser: Browser, company: dict[str, str], *, max_jobs: int, max_pages: int
) -> dict:
    started = datetime.now(timezone.utc).isoformat()
    page = browser.new_page()
    result = {
        "company": company["name"], "careers_url": company["url"],
        "scanned_at": started, "status": "failed", "jobs_found": 0, "jobs": [],
        "pages_visited": [], "error": None, "page_title": "", "page_text_excerpt": "",
        "explicit_no_jobs_message": False, "requires_review": True,
    }
    try:
        page.goto(company["url"], wait_until="domcontentloaded", timeout=30000)
        try:
            page.wait_for_load_state("networkidle", timeout=7000)
        except PlaywrightTimeoutError:
            pass
        page.wait_for_timeout(900)
        result["page_title"] = page.title().strip()
        result["page_text_excerpt"] = _page_text(page)[:1000]
        result["explicit_no_jobs_message"] = any(
            phrase in result["page_text_excerpt"].lower() for phrase in NO_JOBS_PHRASES
        )
        listing_pages = [company["url"]]
        listing_pages.extend(_pagination_urls(page, company["url"])[: max_pages - 1])
        jobs_by_url: dict[str, dict] = {}
        visited_pages = set()
        for listing_url in listing_pages[:max_pages]:
            if _clean_url(listing_url) in visited_pages:
                continue
            visited_pages.add(_clean_url(listing_url))
            result["pages_visited"].append(listing_url)
            if _clean_url(listing_url) != _clean_url(page.url):
                page.goto(listing_url, wait_until="domcontentloaded", timeout=30000)
                try:
                    page.wait_for_load_state("networkidle", timeout=5000)
                except PlaywrightTimeoutError:
                    pass
            current = page.url
            candidates = []
            for link in _page_links(page):
                if _is_job_link(link, current):
                    href = _clean_url(urljoin(current, link["href"]))
                    if href and href not in jobs_by_url:
                        candidates.append((href, link.get("text", "").strip()))
            for href, label in candidates:
                if len(jobs_by_url) >= max_jobs:
                    break
                try:
                    detail = _job_details(page, href, label)
                    detail["listing_title"] = label
                    detail["company"] = company["name"]
                    jobs_by_url[href] = detail
                except Exception as exc:
                    jobs_by_url[href] = {
                        "title": label, "job_url": href, "application_url": href,
                        "description": "", "detail_error": f"{type(exc).__name__}: {str(exc)[:300]}",
                        "company": company["name"], "location": "",
                    }
                page.goto(listing_url, wait_until="domcontentloaded", timeout=30000)
        result["jobs"] = list(jobs_by_url.values())
        result["jobs_found"] = len(result["jobs"])
        if result["jobs_found"]:
            result["status"] = "jobs_found"
            result["requires_review"] = any(not job.get("description") for job in result["jobs"])
        elif result["explicit_no_jobs_message"]:
            result["status"] = "page_says_no_jobs"
        else:
            result["status"] = "no_jobs_detected"
    except Exception as exc:
        result["error"] = f"{type(exc).__name__}: {str(exc)[:500]}"
        result["status"] = "failed"
    finally:
        page.close()
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract vacancies from saved careers-page URLs.")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--company", help="Scan one company by name (case-insensitive).")
    parser.add_argument("--limit", type=int, help="Scan only the first N companies.")
    parser.add_argument("--max-jobs", type=int, default=100, help="Maximum jobs per company.")
    parser.add_argument("--max-pages", type=int, default=5, help="Maximum listing/pagination pages per company.")
    parser.add_argument("--headed", action="store_true", help="Show the browser while scanning.")
    args = parser.parse_args()
    if args.max_jobs < 1 or args.max_pages < 1:
        parser.error("--max-jobs and --max-pages must be at least 1")

    companies = read_companies(args.input)
    if args.company:
        companies = [c for c in companies if c["name"].casefold() == args.company.casefold()]
        if not companies:
            parser.error(f"No company named {args.company!r} exists in {args.input}")
    if args.limit is not None:
        if args.limit < 1:
            parser.error("--limit must be at least 1")
        companies = companies[:args.limit]

    print(f"Scanning {len(companies)} company career page(s). Results: {args.output}")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=not args.headed)
        results = []
        try:
            for index, company in enumerate(companies, start=1):
                print(f"[{index}/{len(companies)}] {company['name']} — {company['url']}")
                result = scan_company(
                    browser, company, max_jobs=args.max_jobs, max_pages=args.max_pages
                )
                results.append(result)
                print(f"    {result['status']}: {result['jobs_found']} job(s)")
        finally:
            browser.close()

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": str(args.input),
        "companies_scanned": len(results),
        "jobs_found_total": sum(item["jobs_found"] for item in results),
        "status_counts": {
            status: sum(item["status"] == status for item in results)
            for status in ("jobs_found", "page_says_no_jobs", "no_jobs_detected", "failed")
        },
        "results": results,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(
        f"Finished: {summary['jobs_found_total']} job(s), "
        f"{summary['status_counts']['failed']} failed page(s)."
    )
    print(f"Full report saved to {args.output}")


if __name__ == "__main__":
    main()
