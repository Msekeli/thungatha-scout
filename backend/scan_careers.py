"""Scan employer careers pages with a real browser and save extracted vacancies locally."""

from __future__ import annotations

import argparse
import json
import re

import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urldefrag, urljoin, urlsplit

from playwright.sync_api import Browser, Page, TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright
from app.application.structured_job_extraction import extract_job_postings

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



def _load_local_env() -> None:
    """Load simple KEY=VALUE settings from backend/.env without overriding shell vars."""
    env_path = ROOT / ".env"
    if not env_path.exists():
        return
    for raw_line in env_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        if key and key not in os.environ:
            os.environ[key] = value


def _gemini_extract_jobs(
    page_text: str,
    links: list[dict[str, str]],
    diagnostics: dict[str, object] | None = None,
) -> list[dict[str, str]]:
    """Use Gemini as a bounded fallback and record a safe diagnostic outcome."""
    diagnostic = diagnostics if diagnostics is not None else {}
    diagnostic["status"] = "not_started"

    if os.getenv("AI_EXTRACTION_ENABLED", "false").lower() != "true":
        diagnostic["status"] = "disabled"
        return []
    if os.getenv("AI_PROVIDER", "gemini").lower() != "gemini":
        diagnostic["status"] = "unsupported_provider"
        return []
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        diagnostic["status"] = "missing_api_key"
        return []

    model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash").strip()
    # Only send a compact page snapshot and links already observed by Playwright.
    observed_links = []
    for item in links[:250]:
        href = item.get("href", "")
        if href.startswith(("https://", "http://")):
            observed_links.append({
                "text": item.get("text", "")[:180],
                "href": href[:1000],
                "job_title": item.get("job_title", "")[:180],
                "location": item.get("location", "")[:180],
                "card_text": item.get("card_text", "")[:700],
            })
    payload = {
        "contents": [{
            "parts": [{
                "text": (
                    "Identify actual vacancy listings on this employer careers page. "
                    "Return JSON only in the shape "
                    '{"jobs":[{"title":"...","job_url":"...","location":"",'
                    '"employment_type":"","evidence":"..."}]}. '
                    "Only return jobs supported by the supplied observed links. "
                    "Copy job_url exactly from an observed link; never invent URLs or jobs. "
                    "Do not return navigation links, categories, talent communities, or generic "
                    "apply links. If uncertain, return an empty jobs array. "
                    "\nPAGE TEXT:\n" + page_text[:10000] +
                    "\nOBSERVED LINKS JSON:\n" + json.dumps(observed_links, ensure_ascii=False)
                )
            }]
        }],
        "generationConfig": {
            "temperature": 0,
            "responseMimeType": "application/json",
            "responseSchema": {
                "type": "OBJECT",
                "properties": {
                    "jobs": {
                        "type": "ARRAY",
                        "items": {
                            "type": "OBJECT",
                            "properties": {
                                "title": {"type": "STRING"},
                                "job_url": {"type": "STRING"},
                                "location": {"type": "STRING"},
                                "employment_type": {"type": "STRING"},
                                "evidence": {"type": "STRING"}
                            },
                            "required": ["title", "job_url", "location", "employment_type", "evidence"]
                        }
                    }
                },
                "required": ["jobs"]
            }
        }
    }
    request = urllib.request.Request(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    diagnostic["status"] = "request_started"
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read(1_000_000).decode("utf-8"))
        text = data["candidates"][0]["content"]["parts"][0]["text"]
        parsed = json.loads(text)
        if not isinstance(parsed, dict) or not isinstance(parsed.get("jobs"), list):
            diagnostic["status"] = "invalid_response"
            return []
    except urllib.error.HTTPError as exc:
        diagnostic["status"] = "api_error"
        diagnostic["http_status"] = exc.code
        return []
    except urllib.error.URLError as exc:
        diagnostic["status"] = "network_error"
        diagnostic["error_type"] = type(exc.reason).__name__
        return []
    except TimeoutError:
        diagnostic["status"] = "timeout"
        return []
    except (KeyError, IndexError, ValueError, TypeError):
        diagnostic["status"] = "invalid_response"
        return []

    diagnostic["jobs_returned"] = len(parsed["jobs"])
    observed = {item.get("href", ""): item for item in observed_links}
    validated = []
    seen = set()
    for job in parsed["jobs"][:50]:
        if not isinstance(job, dict):
            continue
        url = job.get("job_url", "")
        title = re.sub(r"\s+", " ", str(job.get("title", ""))).strip()[:180]
        source = observed.get(url)
        if not source or not title or url in seen:
            continue
        if not url.startswith(("https://", "http://")):
            continue
        seen.add(url)
        validated.append({
            "title": title,
            "listing_title": str(source.get("text", ""))[:180],
            "job_url": url,
            "application_url": "",
            "description": "",
            "location": re.sub(r"\s+", " ", str(job.get("location", ""))).strip()[:180],
            "employment_type": re.sub(r"\s+", " ", str(job.get("employment_type", ""))).strip()[:80],
            "company": "",
            "detail_checked": False,
            "ai_assisted": True,
            "ai_evidence": re.sub(r"\s+", " ", str(job.get("evidence", ""))).strip()[:300],
        })
    diagnostic["jobs_validated"] = len(validated)
    if validated:
        diagnostic["status"] = "success"
    elif parsed["jobs"]:
        diagnostic["status"] = "jobs_rejected_by_validation"
    else:
        diagnostic["status"] = "no_jobs_returned"
    return validated


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


def _split_location_and_employment_type(value: str) -> tuple[str, str]:
    """Separate an employment type joined to the end of listing location text."""
    value = re.sub(r"\s+", " ", value).strip()
    match = re.search(
        r"\s*(Full[- ]Time|Part[- ]Time|Permanent|Contract(?:or)?|Temporary|Internship|Fixed[- ]Term|Casual)\s*$",
        value, re.IGNORECASE,
    )
    if not match:
        return value, ""
    location = value[:match.start()].strip(" ,|-")
    employment_type = match.group(1).replace("-", " ").title()
    return location, employment_type

def _is_job_link(item: dict[str, str], source_url: str) -> bool:
    """Conservatively identify vacancy links without scoring the careers host itself."""
    text = re.sub(r"\s+", " ", item.get("text", "")).strip()
    href = item.get("href", "")
    card = item.get("card_text", "")
    generic_action = text.lower() == "apply now"
    if not text or len(text) > 180:
        return False
    if text.lower() in GENERIC_LINKS and not (generic_action and card):
        return False
    if re.search(
        r"screen readers cannot|searchable map|talent community|how we recruit|"
        r"working at|cookie policy|privacy policy|terms of use",
        text,
        re.I,
    ):
        return False
    parts = urlsplit(href)
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return False
    if _clean_url(href) == _clean_url(source_url):
        return False
    # Never score the hostname: every link on a careers host otherwise looks like a job.
    path = parts.path.lower()
    if re.search(r"/(search|content|about|team|locations?)(/|$)", path):
        return False
    if any(token in path for token in ("/content/", "/talent-community", "/join-talent")):
        return False
    job_path = bool(re.search(
        r"/(job|jobs|position|vacanc|opening|requisition)(/|-|$)|/p/|/go/",
        path,
        re.I,
    ))
    job_text = bool(re.search(
        r"\b(job|vacanc|position|requisition|opening)\b", text, re.I
    ))
    card_evidence = bool(re.search(
        r"\b(remote|hybrid|onsite|full[- ]time|part[- ]time|permanent|"
        r"fixed[- ]term|contract|internship)\b",
        card,
        re.I,
    ))
    action_text = bool(re.search(r"\b(apply|view job|job details)\b", text, re.I))
    # A vacancy needs a job-specific path or a specific title in a job-like card.
    return job_path or (len(text) >= 8 and (job_text or (card_evidence and action_text)))


def _page_links(page: Page) -> list[dict[str, str]]:
    """Read links with nearby card heading and location; never click links here."""
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('a[href]')).map(a => {
          const card = a.closest(
            'article, li, [class*="job"], [class*="position"], ' +
            '[class*="vacan"], [class*="opening"], [class*="listing"], [class*="card"]'
          ) || a.parentElement;
          const heading = card?.querySelector('h1,h2,h3,h4,[class*="title"],[class*="name"]');
          const lines = (card?.innerText || '').split('\\n').map(x => x.trim()).filter(Boolean);
          const location = lines.find(x => /cape town|brackenfell|south africa|remote|hybrid|johannesburg|durban|pretoria/i.test(x)) || '';
          return {
            text: (a.innerText || a.getAttribute('aria-label') || a.title || '').trim(),
            href: a.href,
            job_title: (heading?.innerText || '').trim(),
            location,
            card_text: (card?.innerText || a.parentElement?.innerText || '').trim().slice(0, 1200)
          };
        })"""
    )


def _try_location_search(page: Page, location: str = "Cape Town") -> bool:
    """Use a visible location search only when a matching field is present."""
    fields = page.locator(
        'input[placeholder*="location" i], input[aria-label*="location" i], '
        'input[name*="location" i], input[id*="location" i]'
    )
    try:
        for index in range(min(fields.count(), 5)):
            field = fields.nth(index)
            if not field.is_visible():
                continue
            field.fill(location, timeout=1500)
            # Prefer an explicit search/filter submit control; do not click Apply.
            buttons = page.locator(
                'button[type="submit"], input[type="submit"], button:has-text("Search"), '
                'button:has-text("Filter")'
            )
            for button_index in range(min(buttons.count(), 5)):
                button = buttons.nth(button_index)
                if button.is_visible() and button.is_enabled():
                    button.click(timeout=1500)
                    page.wait_for_timeout(500)
                    return True
            field.press("Enter", timeout=1000)
            page.wait_for_timeout(500)
            return True
    except Exception:
        return False
    return False


def _page_text(page: Page) -> str:
    try:
        return page.locator("body").inner_text(timeout=4000).strip()
    except Exception:
        return ""


def _job_details(page: Page, url: str, listing_text: str) -> dict[str, str]:
    page.goto(url, wait_until="domcontentloaded", timeout=10000)
    page.set_default_timeout(1500)
    page.wait_for_timeout(250)
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
                r"\b(cape town|south africa|remote|hybrid|johannesburg|durban|pretoria|"
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
        "application_url": apply_url,
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



def _sanlam_listing_links(page: Page, source_url: str) -> list[dict[str, str]]:
    """Extract Sanlam vacancy cards only; do not interact with application controls."""
    return page.evaluate(
        """(sourceUrl) => {
          const ignored = new Set([
            'careers', 'working at sanlam', 'how we recruit', 'join talent community',
            'get job alerts for this search', 'log-in', 'login', 'search jobs'
          ]);
          const seen = new Set();
          return Array.from(document.querySelectorAll('a[href]')).flatMap(a => {
            const text = (a.innerText || a.getAttribute('aria-label') || a.title || '')
              .replace(/\\s+/g, ' ').trim();
            const url = new URL(a.href, location.href);
            if (!text || text.length < 8 || text.length > 180 ||
                ignored.has(text.toLowerCase()) || seen.has(url.href) ||
                url.origin !== location.origin || !/^\\/go\\//i.test(url.pathname)) return [];
            let card = a.closest('article, li, [class*="job"], [class*="result"], [class*="card"]');
            if (!card || card.innerText.trim().length < 20) card = a.parentElement;
            const cardText = (card?.innerText || '').replace(/\\s+/g, ' ').trim();
            if (!cardText || cardText.length < 20) return [];
            seen.add(url.href);
            const locationMatch = cardText.match(/(?:Cape Town|Western Cape|South Africa|Remote|Hybrid)[^•]*/i);
            return [{
              text,
              href: url.href,
              job_title: text,
              location: locationMatch ? locationMatch[0].trim().slice(0, 180) : '',
              card_text: cardText.slice(0, 1200)
            }];
          });
        }""",
        source_url,
    )


def scan_company(
    browser: Browser, company: dict[str, str], *, max_jobs: int, max_pages: int
) -> dict:
    started = datetime.now(timezone.utc).isoformat()
    page = browser.new_page()
    page.set_default_navigation_timeout(12000)
    page.set_default_timeout(1800)
    result = {
        "company": company["name"], "careers_url": company["url"],
        "scanned_at": started, "status": "failed", "jobs_found": 0, "jobs": [],
        "pages_visited": [], "error": None, "page_title": "", "page_text_excerpt": "",
        "explicit_no_jobs_message": False, "requires_review": True,
    }
    try:
        page.set_default_navigation_timeout(12000)
        page.set_default_timeout(1800)
        is_sanlam = company["name"].casefold() == "sanlam"
        source_url = (
            "https://careers.sanlamcloud.co.za/search/?q=&locationsearch=Cape+Town&searchResultView=LIST"
            if is_sanlam else company["url"]
        )
        page.goto(source_url, wait_until="domcontentloaded", timeout=12000)
        # Sanlam renders its search results in a dedicated results view; allow it to settle.
        page.wait_for_timeout(1600 if is_sanlam else 500)
        location_filtered = False if is_sanlam else _try_location_search(page)
        result["location_filter_attempted"] = location_filtered
        result["page_title"] = page.title().strip()
        page_text = _page_text(page)
        result["page_text_excerpt"] = page_text[:1000]
        result["explicit_no_jobs_message"] = any(
            phrase in page_text.lower() for phrase in NO_JOBS_PHRASES
        )
        # Follow explicit job-search entry points, not every career-site link.
        listing_pages = [source_url]
        initial_links = _sanlam_listing_links(page, source_url) if is_sanlam else _page_links(page)
        for link in initial_links:
            href = link.get("href", "")
            path = urlsplit(href).path.lower()
            if re.search(r"(^|/)(search|jobs-search|job-search|vacancies)(/|$)", path):
                if href.startswith(("https://", "http://")) and all(
                    _clean_url(href) != _clean_url(item) for item in listing_pages
                ):
                    listing_pages.append(href)
        for url in _pagination_urls(page, company["url"]):
            if all(_clean_url(url) != _clean_url(item) for item in listing_pages):
                listing_pages.append(url)
        jobs_by_url: dict[str, dict] = {}
        visited_pages = set()
        page_index = 0
        while page_index < min(len(listing_pages), max_pages):
            listing_url = listing_pages[page_index]
            page_index += 1
            if _clean_url(listing_url) in visited_pages:
                continue
            visited_pages.add(_clean_url(listing_url))
            result["pages_visited"].append(listing_url)
            if _clean_url(listing_url) != _clean_url(page.url):
                page.goto(listing_url, wait_until="domcontentloaded", timeout=12000)
                page.wait_for_timeout(500)
            # Search pages often hold vacancies behind a keyword/location form.
            if _clean_url(page.url) != _clean_url(company["url"]):
                _try_location_search(page, "Cape Town")
                page.wait_for_timeout(700)
            current = page.url
            # Structured data is the first extraction layer; keep the page URL as provenance.
            try:
                structured_jobs = extract_job_postings(
                    page.content(), current, company["name"]
                )
            except Exception as exc:
                structured_jobs = []
                result.setdefault("extraction_warnings", []).append(
                    f"structured_data:{type(exc).__name__}"
                )
            for structured in structured_jobs:
                href = _clean_url(structured["job_url"])
                if not href:
                    continue
                candidate = {
                    "title": structured["title"],
                    "listing_title": structured["title"],
                    "job_url": href,
                    "application_url": "",
                    "description": structured.get("description", ""),
                    "location": ", ".join(structured.get("locations", [])),
                    "employment_type": structured.get("employment_type", ""),
                    "company": company["name"],
                    "detail_checked": False,
                    "source_type": structured["source_type"],
                    "source_page_url": structured["source_page_url"],
                    "evidence": structured["evidence"],
                    "date_posted": structured.get("date_posted", ""),
                    "valid_through": structured.get("valid_through", ""),
                }
                existing = jobs_by_url.get(href)
                if existing:
                    for key, value in candidate.items():
                        if value and not existing.get(key):
                            existing[key] = value
                else:
                    jobs_by_url[href] = candidate
                    print(
                        f"        Structured listing {len(jobs_by_url)}: {candidate['title']}",
                        flush=True,
                    )
            for next_url in _pagination_urls(page, current):
                if _clean_url(next_url) not in visited_pages and all(
                    _clean_url(next_url) != _clean_url(item) for item in listing_pages
                ):
                    listing_pages.append(next_url)
            page_links = _sanlam_listing_links(page, current) if is_sanlam else _page_links(page)
            for link in page_links:
                if is_sanlam:
                    link_path = urlsplit(link.get("href", "")).path.lower()
                    if not link_path.startswith("/go/"):
                        continue
                elif not _is_job_link(link, current):
                    continue
                href = _clean_url(urljoin(current, link["href"]))
                label = (link.get("job_title") or link.get("text") or "").strip()
                if not href or href in jobs_by_url:
                    continue
                # Exclude platform/navigation links and generic Apply buttons without a job-like URL.
                path = urlsplit(href).path.lower()
                if any(token in path for token in ("/team/portal", "/m/portal")):
                    continue
                if not is_sanlam and not re.search(r"/p/|/job|/jobs|/position|/vacan|/go/", path) and label.lower() in {"apply", "apply now"}:
                    continue
                if label.lower() in {"apply", "apply now", "powered by breezy"}:
                    slug = path.rsplit("/", 1)[-1]
                    label = re.sub(r"^[0-9a-f-]{8,}-", "", slug).replace("-", " ").strip().title()
                if not label or label.lower() in {"powered by breezy", "shopritex referral portal"}:
                    continue
                location, employment_type = _split_location_and_employment_type(
                    link.get("location", "")
                )
                jobs_by_url[href] = {
                    "title": label,
                    "listing_title": link.get("text", "").strip(),
                    "job_url": href,
                    "application_url": "",
                    "description": "",
                    "location": location,
                    "employment_type": employment_type,
                    "company": company["name"],
                    "detail_checked": False,
                }
                print(f"        Listing {len(jobs_by_url)}: {label}", flush=True)
                if len(jobs_by_url) >= max_jobs:
                    break
        result["jobs"] = list(jobs_by_url.values())
        _load_local_env()
        if not result["jobs"] and os.getenv("AI_EXTRACTION_ENABLED", "false").lower() == "true":
            diagnostics: dict[str, object] = {}
            try:
                ai_jobs = _gemini_extract_jobs(
                    _page_text(page), _page_links(page), diagnostics
                )
                for job in ai_jobs:
                    job["company"] = company["name"]
                result["jobs"] = ai_jobs[:max_jobs]
                result["ai_fallback_attempted"] = diagnostics.get("status") not in {
                    "disabled", "unsupported_provider", "missing_api_key", "not_started"
                }
                result["ai_fallback_jobs"] = len(result["jobs"])
                result["ai_fallback_status"] = diagnostics.get("status", "unknown")
                result["ai_fallback_diagnostics"] = diagnostics
            except Exception as exc:
                result["ai_fallback_attempted"] = True
                result["ai_fallback_status"] = "unexpected_error"
                result["ai_fallback_error"] = f"{type(exc).__name__}: {str(exc)[:250]}"
        result["jobs_found"] = len(result["jobs"])
        if result["jobs_found"]:
            result["status"] = "jobs_found"
            result["requires_review"] = any(
                not job.get("description") or not job.get("location")
                or not job.get("application_url") for job in result["jobs"]
            )
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
    parser.add_argument("--max-jobs", type=int, default=20, help="Maximum listing records per company (default: 20).")
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

    all_jobs = [
        job for company_result in results for job in company_result.get("jobs", [])
    ]
    source_counts: dict[str, int] = {}
    for job in all_jobs:
        source_type = job.get("source_type", "dom_link")
        source_counts[source_type] = source_counts.get(source_type, 0) + 1

    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "input_file": str(args.input),
        "companies_scanned": len(results),
        "jobs_found_total": len(all_jobs),
        "status_counts": {
            status: sum(item["status"] == status for item in results)
            for status in ("jobs_found", "page_says_no_jobs", "no_jobs_detected", "failed")
        },
        "job_quality_counts": {
            "with_description": sum(bool(job.get("description")) for job in all_jobs),
            "with_location": sum(bool(job.get("location")) for job in all_jobs),
            "with_application_url": sum(bool(job.get("application_url")) for job in all_jobs),
            "requiring_review": sum(bool(
                not job.get("description") or not job.get("location")
                or not job.get("application_url")
            ) for job in all_jobs),
        },
        "extraction_source_counts": source_counts,
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
