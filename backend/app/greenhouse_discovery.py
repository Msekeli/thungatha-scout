"""Automated discovery and validation of public Greenhouse job boards.

Search results are untrusted leads. A board is registered only after its public
Greenhouse API returns a valid jobs payload with usable job records. The
discovery pass also inspects a bounded number of official/company result pages
for publicly embedded Greenhouse board references.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx
from ddgs import DDGS

from app.site_investigator import USER_AGENT, _normalise_job

# Diverse query patterns are intentional: search engines interpret complex
# Boolean expressions inconsistently, so use several narrow query families.
DEFAULT_QUERIES = (
    'site:job-boards.greenhouse.io',
    'site:boards.greenhouse.io',
    'site:job-boards.greenhouse.io "South Africa"',
    'site:job-boards.greenhouse.io "Cape Town"',
    'site:job-boards.greenhouse.io "Remote"',
    'site:job-boards.greenhouse.io engineer',
    'site:job-boards.greenhouse.io developer',
    'site:job-boards.greenhouse.io software',
    'site:boards.greenhouse.io "South Africa"',
    'site:boards.greenhouse.io "Cape Town"',
    'site:boards.greenhouse.io engineer',
    'site:boards.greenhouse.io developer',
    '"boards-api.greenhouse.io/v1/boards/"',
    '"boards.greenhouse.io/embed/job_app?for="',
    '"job-boards.greenhouse.io" careers',
    '"boards.greenhouse.io" careers software jobs',
    '"Greenhouse" "careers" "South Africa" software company',
    '"powered by Greenhouse" careers technology',
    '"boards-api.greenhouse.io" jobs careers',
    'site:greenhouse.io "South Africa" jobs',
)
BOARD_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
RESERVED_PATHS = {"embed", "jobs", "job", "search", "login", "signup", "privacy", "terms"}
API_TOKEN_RE = re.compile(
    r"boards-api[.]greenhouse[.]io/v1/boards/([A-Za-z0-9_-]{2,80})", re.I
)
PUBLIC_BOARD_URL_RE = re.compile(
    r"""https?://(?:job-)?boards[.]greenhouse[.]io/[^ \t\r\n"'<>]+""", re.I
)
DEFAULT_PAGE_INSPECTION_LIMIT = 80


def _valid_token(token: str) -> str | None:
    token = token.strip().rstrip("/.,;)")
    if token.lower() in RESERVED_PATHS or not re.fullmatch(r"[A-Za-z0-9_-]{2,80}", token):
        return None
    return token


def board_token_from_url(url: str) -> str | None:
    """Extract a plausible board token only from known public Greenhouse URLs."""
    try:
        parsed = urlparse(url)
    except ValueError:
        return None
    host = (parsed.hostname or "").lower()
    if host not in BOARD_HOSTS:
        return None
    query = parse_qs(parsed.query)
    if query.get("for"):
        return _valid_token(query["for"][0])
    parts = [part for part in parsed.path.split("/") if part]
    if not parts:
        return None
    return _valid_token(parts[0])


def greenhouse_tokens_from_html(html: str) -> list[str]:
    """Find explicit public Greenhouse references in HTML/source text."""
    found: dict[str, str] = {}
    for token in API_TOKEN_RE.findall(html):
        valid = _valid_token(token)
        if valid:
            found.setdefault(valid.casefold(), valid)
    # Unescape common HTML/JS URL separators before parsing public board links.
    source = html.replace(r"\\/", "/").replace("&amp;", "&")
    for match in PUBLIC_BOARD_URL_RE.findall(source):
        cleaned = match.rstrip(").,;]}")
        token = board_token_from_url(cleaned)
        if token:
            found.setdefault(token.casefold(), token)
    # Embed URLs may be relative or stored as a URL fragment in a JS string.
    for match in re.findall(
        r"(?:boards\\.greenhouse\\.io/)?embed/job_app\\?[^\\s\"'<>]*for=([A-Za-z0-9_-]{2,80})",
        source,
        re.I,
    ):
        valid = _valid_token(match)
        if valid:
            found.setdefault(valid.casefold(), valid)
    return list(found.values())


def validate_greenhouse_board(
    client: httpx.Client, token: str, *, max_jobs: int = 100
) -> dict[str, Any]:
    """Validate a board against the public API and reject malformed/empty feeds."""
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    result: dict[str, Any] = {
        "board_token": token,
        "board_url": f"https://job-boards.greenhouse.io/{token}",
        "api_url": endpoint,
        "validated_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": None,
        "valid": False,
        "total_jobs_reported": 0,
        "usable_jobs": 0,
        "jobs": [],
        "error": "",
    }
    try:
        response = client.get(endpoint)
        result["http_status"] = response.status_code
        if not response.is_success:
            result["error"] = f"Public board API returned HTTP {response.status_code}"
            return result
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            result["error"] = "API response did not contain a jobs array."
            return result
        raw_jobs = payload["jobs"]
        result["total_jobs_reported"] = len(raw_jobs)
        jobs: list[dict[str, Any]] = []
        seen_ids: set[str] = set()
        for raw in raw_jobs:
            if not isinstance(raw, dict):
                continue
            title = str(raw.get("title") or "").strip()
            job_id = str(raw.get("id") or "").strip()
            job_url = str(raw.get("absolute_url") or "").strip()
            if not title or not job_id or not job_url.startswith("https://"):
                continue
            if job_id in seen_ids:
                continue
            seen_ids.add(job_id)
            job = _normalise_job(raw, "greenhouse")
            job["id"] = job_id
            jobs.append(job)
        result["jobs"] = jobs[:max_jobs]
        result["usable_jobs"] = len(jobs)
        result["valid"] = bool(jobs)
        if not jobs:
            result["error"] = "API responded successfully but returned no usable, uniquely identified jobs."
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def discover_greenhouse_boards(
    *,
    max_results_per_query: int = 20,
    backend: str = "auto",
    queries: tuple[str, ...] = DEFAULT_QUERIES,
    timeout: float = 20.0,
    page_inspection_limit: int = DEFAULT_PAGE_INSPECTION_LIMIT,
) -> dict[str, Any]:
    """Search board URLs and company pages, inspect explicit references, then validate feeds.

    Coverage depends on public search indexing and may be rate-limited. Only
    explicitly observed tokens are tested; tokens are never guessed from names.
    """
    if max_results_per_query < 1:
        raise ValueError("max_results_per_query must be at least 1")
    if page_inspection_limit < 0:
        raise ValueError("page_inspection_limit must be at least 0")

    candidates: dict[str, dict[str, Any]] = {}
    source_pages: dict[str, dict[str, Any]] = {}
    search_errors: list[str] = []
    successful_queries = 0
    search = DDGS(timeout=timeout)

    def add_candidate(token: str, source_url: str, query: str, title: str = "",
                      snippet: str = "", method: str = "search-result-url") -> None:
        token = _valid_token(token) or ""
        if not token:
            return
        key = token.casefold()
        entry = candidates.setdefault(key, {
            "board_token": token,
            "candidate_urls": [],
            "search_evidence": [],
            "discovery_methods": [],
        })
        if source_url and source_url not in entry["candidate_urls"]:
            entry["candidate_urls"].append(source_url)
        evidence = {"query": query, "title": title, "snippet": snippet}
        if evidence not in entry["search_evidence"]:
            entry["search_evidence"].append(evidence)
        if method not in entry["discovery_methods"]:
            entry["discovery_methods"].append(method)

    for query in dict.fromkeys(queries):
        try:
            results = search.text(
                query,
                region="wt-wt",
                safesearch="moderate",
                max_results=max_results_per_query,
                backend=backend,
            )
            successful_queries += 1
        except Exception as exc:
            search_errors.append(f"{query}: {exc}")
            continue

        for item in results or []:
            url = str(item.get("href") or item.get("url") or "").strip()
            if not url.startswith(("http://", "https://")):
                continue
            title = str(item.get("title") or "").strip()
            snippet = str(item.get("body") or item.get("snippet") or "").strip()
            token = board_token_from_url(url)
            if token:
                add_candidate(token, url, query, title, snippet)
                continue

            parsed = urlparse(url)
            host = (parsed.hostname or "").lower()
            if host in BOARD_HOSTS:
                continue
            # Search results for employer career pages can reveal embedded
            # Greenhouse tokens even when the result URL is not Greenhouse.
            source_pages.setdefault(url, {
                "url": url, "query": query, "title": title, "snippet": snippet,
            })

    inspected_pages = 0
    page_errors: list[str] = []
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"},
    ) as client:
        for page in list(source_pages.values())[:page_inspection_limit]:
            try:
                response = client.get(page["url"])
                if not response.is_success:
                    page_errors.append(f"{page['url']}: HTTP {response.status_code}")
                    continue
                inspected_pages += 1
                content_type = response.headers.get("content-type", "").lower()
                if content_type and "html" not in content_type and "text" not in content_type:
                    continue
                html = response.text
                for token in greenhouse_tokens_from_html(html):
                    add_candidate(
                        token, page["url"], page["query"], page["title"], page["snippet"],
                        method="embedded-reference",
                    )
            except (httpx.HTTPError, UnicodeError) as exc:
                page_errors.append(f"{page['url']}: {exc}")

        boards: list[dict[str, Any]] = []
        # Reuse the same client; API requests are only made for explicit tokens.
        for candidate in candidates.values():
            validation = validate_greenhouse_board(client, candidate["board_token"])
            boards.append({**candidate, **validation})

    boards.sort(key=lambda item: (not item["valid"], item["board_token"].casefold()))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "search_queries": list(dict.fromkeys(queries)),
        "successful_queries": successful_queries,
        "failed_queries": search_errors,
        "search_result_pages_seen": len(source_pages),
        "company_pages_inspected": inspected_pages,
        "company_page_inspection_limit": page_inspection_limit,
        "company_page_errors": page_errors,
        "candidate_boards_found": len(candidates),
        "validated_boards_found": sum(1 for board in boards if board["valid"]),
        "boards": boards,
        "limitations": [
            "Discovery is limited to public search results and is not an exhaustive list of Greenhouse customers.",
            "Company-page inspection is bounded and may miss pages beyond the inspection limit.",
            "A valid public board proves the feed is accessible, not that every job is relevant to a target region.",
            "Search engines may rate-limit requests or change indexing; rerun periodically to discover newly indexed boards.",
            "Only public pages and the public Greenhouse jobs API are requested; no authentication or access controls are bypassed.",
        ],
    }


def save_greenhouse_discovery_report(
    report: dict[str, Any], output_dir: str | Path
) -> tuple[Path, Path]:
    """Save JSON evidence and a compact CSV registry, separate from companies.csv."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = out / f"greenhouse-discovery-{stamp}.json"
    csv_path = out / f"greenhouse-board-registry-{stamp}.csv"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        fields = [
            "board_token", "board_url", "api_url", "valid", "http_status",
            "total_jobs_reported", "usable_jobs", "error", "candidate_urls",
            "discovery_methods",
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for board in report.get("boards", []):
            if not board.get("valid"):
                continue
            writer.writerow({
                key: json.dumps(board.get(key), ensure_ascii=False)
                if key in {"candidate_urls", "discovery_methods"} else board.get(key, "")
                for key in fields
            })
    return json_path, csv_path
"