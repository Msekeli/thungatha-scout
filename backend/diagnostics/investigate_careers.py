"""Investigate how configured employer career pages expose vacancies.

Run from backend/: python diagnostics/investigate_careers.py
    [--input cape_town_tech_companies.json] [--output investigation_report.json]
This is a diagnostic only: it never publishes vacancies or calls an AI provider.
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path
from urllib.parse import urlparse

from playwright.sync_api import sync_playwright
from app.application.structured_job_extraction import extract_job_postings

ROOT = Path(__file__).resolve().parents[1]
TITLE_KEYS = {"title", "jobtitle", "job_title", "positiontitle", "name"}
URL_KEYS = {"url", "joburl", "link", "absolute_url", "applyurl", "detailurl"}
ID_KEYS = {"id", "jobid", "reqid", "requisitionid", "referencenumber"}
LOCATION_KEYS = {"location", "locations", "city", "joblocation", "primarylocation"}
SIGNAL_KEYS = LOCATION_KEYS | {
    "department", "employmenttype", "jobtype", "posteddate", "dateposted", "category"
}
NAV_TITLE = re.compile(
    r"^(home|about|contact|login|log in|sign in|register|careers|jobs|search|"
    r"menu|privacy|terms|news|blog|faq|help)$", re.I
)
LINK_HINT = re.compile(
    r"open (positions|roles)|view (all )?(jobs|openings|vacancies|positions)|"
    r"search jobs|current (openings|vacancies)|vacancies|join us|careers|jobs",
    re.I,
)
BLOCK = re.compile(
    r"captcha|verify you are human|access denied|attention required|are you a robot",
    re.I,
)
NO_JOBS = re.compile(
    r"no (open )?(jobs|vacancies|positions|results)|0 (jobs|results)|no matching",
    re.I,
)
PLATFORMS = {
    "workday": r"myworkdayjobs",
    "successfactors": r"successfactors|jobs2web|sapsf",
    "oracle": r"oraclecloud|taleo",
    "greenhouse": r"greenhouse\.io|job-boards\.greenhouse",
    "lever": r"lever\.co",
    "breezy": r"breezy\.hr",
    "smartrecruiters": r"smartrecruiters",
    "workable": r"workable\.com",
}


def _pick(item: dict, keys: set[str]):
    lowered = {str(key).lower(): value for key, value in item.items()}
    return next((lowered[key] for key in keys if lowered.get(key) not in (None, "", [], {})), None)


def validate_job_list(data) -> list[dict]:
    """Accept a candidate JSON array only when its items resemble actual vacancies."""
    candidates = []

    def walk(value):
        if isinstance(value, list):
            if value and all(isinstance(item, dict) for item in value[:5]):
                candidates.append(value)
            for item in value[:100]:
                walk(item)
        elif isinstance(value, dict):
            for child in value.values():
                walk(child)

    walk(data)
    best = []
    for items in candidates:
        jobs, signals = [], 0
        for item in items:
            title = _pick(item, TITLE_KEYS)
            title = re.sub(r"\s+", " ", title).strip() if isinstance(title, str) else ""
            url, ref = _pick(item, URL_KEYS), _pick(item, ID_KEYS)
            if not 4 <= len(title) <= 150 or NAV_TITLE.fullmatch(title) or not (url or ref):
                continue
            location = _pick(item, LOCATION_KEYS)
            if location or _pick(item, SIGNAL_KEYS - TITLE_KEYS - URL_KEYS - ID_KEYS):
                signals += 1
            jobs.append({"title": title, "location": location, "url": url, "id": ref})
        unique_titles = {job["title"].casefold() for job in jobs}
        # A single well-shaped record is useful evidence too; requiring two
        # records misses small employers and filtered search results.
        enough_evidence = (
            len(jobs) == 1 and signals == 1
            or len(jobs) >= 2
            and len(unique_titles) >= .7 * len(jobs)
            and len(jobs) >= .6 * len(items)
            and signals >= .4 * len(jobs)
        )
        if enough_evidence and len(jobs) > len(best):
            best = jobs
    return best


def _jsonld(html: str, page_url: str, company: str) -> list[dict]:
    return extract_job_postings(html, page_url, company)


def _try_search(page) -> dict:
    result = {"location_filled": False, "submitted": False}
    try:
        location = page.locator(
            "input[placeholder*='ocation' i], input[aria-label*='ocation' i], "
            "input[name*='ocation' i], input[id*='ocation' i], "
            "input[placeholder*='city' i], input[placeholder*='where' i]"
        )
        if not location.count():
            return result
        location.first.fill("Cape Town")
        result["location_filled"] = True
        try:
            option = page.get_by_role("option").first
            option.wait_for(timeout=1200)
            option.click()
        except Exception:
            pass
        button = page.get_by_role("button", name=re.compile(r"search|find", re.I))
        if button.count():
            button.first.click(timeout=3000)
            result["submitted"] = True
        else:
            location.first.press("Enter")
            result["submitted"] = True
        try:
            page.wait_for_load_state("networkidle", timeout=10000)
        except Exception:
            page.wait_for_timeout(1500)
    except Exception as exc:
        result["error"] = type(exc).__name__
    return result


def _next_link(page, visited: set[str]):
    anchors = page.evaluate(
        "() => [...document.querySelectorAll('a[href]')].map(a => "
        "({text:(a.innerText||'').trim().slice(0,100), href:a.href}))"
    )
    ranked = []
    for anchor in anchors:
        href = anchor["href"].split("#", 1)[0]
        if (href.startswith(("http://", "https://")) and href not in visited
                and LINK_HINT.search(anchor["text"] + " " + href)):
            ranked.append((bool(re.search(r"careers|jobs|vacanc|position", anchor["text"], re.I)), href))
    return max(ranked, default=(False, None))[1]


def investigate(browser, company: str, start_url: str, max_pages: int = 3) -> dict:
    context = browser.new_context(user_agent="ThungathaScout-diagnostic/0.2")
    page = context.new_page()
    hits, path, visited, page_evidence = [], [], set(), []
    result = {
        "company": company, "start_url": start_url, "status": "unresolved",
        "path": path, "pages": page_evidence, "platform": [], "search": None,
        "endpoint": None, "job_count": 0, "jobs": [], "jsonld": False,
    }

    def on_response(response):
        try:
            request = response.request
            if request.resource_type not in {"xhr", "fetch"}:
                return
            if "json" not in response.headers.get("content-type", "").lower():
                return
            jobs = validate_job_list(response.json())
            if jobs:
                hits.append({
                    "url": response.url, "method": request.method,
                    "post_data": request.post_data, "jobs": jobs,
                    "request_headers": {
                        key: value for key, value in request.headers.items()
                        if key.lower() in {"accept", "content-type"}
                    },
                })
        except Exception:
            return

    page.on("response", on_response)
    try:
        for _ in range(max_pages):
            if not start_url or start_url in visited:
                break
            target = start_url
            visited.add(target)
            path.append(target)
            try:
                response = page.goto(target, wait_until="domcontentloaded", timeout=25000)
                try:
                    page.wait_for_load_state("networkidle", timeout=8000)
                except Exception:
                    page.wait_for_timeout(1200)
            except Exception as exc:
                result.update(status="load_failed", error=type(exc).__name__)
                break
            status_code = response.status if response else None
            html = page.content()
            try:
                heading = page.locator("h1").first.inner_text(timeout=1000).strip()
            except Exception:
                heading = ""
            try:
                page_title = page.title()
            except Exception:
                page_title = ""
            try:
                body_text = page.locator("body").inner_text(timeout=2000)
            except Exception:
                body_text = ""
            page_evidence.append({
                "url": page.url, "http_status": status_code,
                "title": page_title[:200], "h1": heading[:200],
                "body_excerpt": re.sub(r"\\s+", " ", body_text)[:600],
            })
            if status_code in {404, 410}:
                result["status"] = "dead_url"
                break
            if status_code in {401, 403, 429} or BLOCK.search(html[:8000]):
                result["status"] = "blocked"
                break
            result["platform"] = sorted({
                name for name, pattern in PLATFORMS.items()
                if re.search(pattern, html + " " + page.url, re.I)
            })
            jobs = _jsonld(html, page.url, company)
            if jobs:
                result.update(status="jobs_in_jsonld", jsonld=True,
                              job_count=len(jobs), jobs=jobs[:30])
                break
            if not hits:
                result["search"] = _try_search(page)
                html = page.content()
                jobs = _jsonld(html, page.url, company)
                if jobs:
                    result.update(status="jobs_in_jsonld", jsonld=True,
                                  job_count=len(jobs), jobs=jobs[:30])
                    break
            if hits:
                best = max(hits, key=lambda hit: len(hit["jobs"]))
                replayed = False
                try:
                    replay = context.request.fetch(
                        best["url"], method=best["method"], data=best["post_data"],
                        headers=best["request_headers"], timeout=10000,
                    )
                    replayed = replay.ok and bool(validate_job_list(replay.json()))
                except Exception:
                    pass
                result.update(
                    status="jobs_via_network_json" if replayed else "endpoint_not_replayable",
                    endpoint=best["url"], endpoint_host=urlparse(best["url"]).netloc,
                    method=best["method"], post_data=best["post_data"],
                    replayed=replayed, job_count=len(best["jobs"]), jobs=best["jobs"][:30],
                )
                break
            try:
                body = page.locator("body").inner_text(timeout=3000)
            except Exception:
                body = ""
            if NO_JOBS.search(body[:20000]):
                result["status"] = "page_says_no_jobs"
                break
            nxt = _next_link(page, visited)
            if not nxt:
                break
            start_url = nxt
        if result["status"] == "unresolved":
            detail_pages = [
                item for item in page_evidence
                if re.search(r"/careers?/[^/?#]+", urlparse(item["url"]).path, re.I)
                and (item["h1"] or item["title"])
            ]
            if detail_pages:
                result["status"] = "job_detail_pages_detected_no_structured_jobs"
                result["job_detail_pages"] = [
                    {"url": item["url"], "title": item["title"], "h1": item["h1"]}
                    for item in detail_pages
                ]
            elif result.get("search"):
                result["status"] = (
                    "search_failed" if result["search"].get("submitted")
                    else "search_control_not_found"
                )
            else:
                result["status"] = "unresolved_no_job_evidence"
    finally:
        context.close()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=ROOT / "cape_town_tech_companies.json")
    parser.add_argument("--output", type=Path, default=ROOT / "investigation_report.json")
    parser.add_argument("--max-pages", type=int, default=3)
    parser.add_argument("--delay", type=float, default=1.0, help="Seconds between companies")
    parser.add_argument(
        "--company",
        help="Investigate only the company whose name matches this text (case-insensitive).",
    )
    args = parser.parse_args()
    if not 1 <= args.max_pages <= 3:
        parser.error("--max-pages must be between 1 and 3")
    companies = json.loads(args.input.read_text(encoding="utf-8"))
    if args.company:
        companies = [
            company for company in companies
            if args.company.casefold() in company["name"].casefold()
        ]
        if not companies:
            parser.error(f"No company name matched: {args.company}")
    report, counts = [], {}
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        try:
            for company in companies:
                item = investigate(
                    browser, company["name"], company.get("careers_url") or company["url"],
                    args.max_pages,
                )
                print(f"{item['status']:<26} {item['company']}")
                report.append(item)
                counts[item["status"]] = counts.get(item["status"], 0) + 1
                time.sleep(max(0, min(args.delay, 5)))
        finally:
            browser.close()
    args.output.write_text(json.dumps({
        "generated_at": __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        ).isoformat(),
        "input_file": str(args.input), "companies_scanned": len(report),
        "status_counts": counts, "results": report,
    }, indent=2), encoding="utf-8")
    print(f"Report: {args.output}")
    print(json.dumps(counts, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
