"""Automated discovery and validation of public Greenhouse job boards.

Search results are untrusted leads. A board is registered only after its public
Greenhouse API returns a valid jobs payload with usable job records.
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

DEFAULT_QUERIES = (
    'site:job-boards.greenhouse.io software OR engineering',
    'site:boards.greenhouse.io software OR engineering',
    'site:job-boards.greenhouse.io "South Africa" OR "Cape Town"',
    '"boards-api.greenhouse.io/v1/boards" careers jobs',
)
BOARD_HOSTS = {"boards.greenhouse.io", "job-boards.greenhouse.io"}
RESERVED_PATHS = {"embed", "jobs", "job", "search", "login", "signup", "privacy", "terms"}


def board_token_from_url(url: str) -> str | None:
    """Extract a plausible board token only from known public Greenhouse URLs."""
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if host not in BOARD_HOSTS:
        return None
    query = parse_qs(parsed.query)
    if query.get("for"):
        token = query["for"][0]
    else:
        parts = [part for part in parsed.path.split("/") if part]
        if not parts:
            return None
        token = parts[0]
    token = token.strip()
    if token.lower() in RESERVED_PATHS or not re.fullmatch(r"[A-Za-z0-9_-]{2,80}", token):
        return None
    return token


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
) -> dict[str, Any]:
    """Search for public board URLs, validate tokens, and return deduplicated boards.

    Search coverage depends on public search indexing and may be rate-limited.
    The function never guesses tokens from company names and never touches the
    existing companies.csv file.
    """
    if max_results_per_query < 1:
        raise ValueError("max_results_per_query must be at least 1")
    candidates: dict[str, dict[str, Any]] = {}
    search_errors: list[str] = []
    successful_queries = 0
    search = DDGS(timeout=timeout)
    for query in queries:
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
            token = board_token_from_url(url)
            if not token:
                # Some search results expose an embed URL rather than a board URL.
                parsed = urlparse(url)
                if (parsed.hostname or "").lower() in BOARD_HOSTS:
                    continue
                continue
            key = token.casefold()
            entry = candidates.setdefault(key, {
                "board_token": token,
                "candidate_urls": [],
                "search_evidence": [],
            })
            if url not in entry["candidate_urls"]:
                entry["candidate_urls"].append(url)
            evidence = {
                "query": query,
                "title": str(item.get("title") or "").strip(),
                "snippet": str(item.get("body") or item.get("snippet") or "").strip(),
            }
            if evidence not in entry["search_evidence"]:
                entry["search_evidence"].append(evidence)

    boards: list[dict[str, Any]] = []
    with httpx.Client(
        follow_redirects=True,
        timeout=timeout,
        headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
    ) as client:
        for candidate in candidates.values():
            validation = validate_greenhouse_board(client, candidate["board_token"])
            boards.append({**candidate, **validation})
    boards.sort(key=lambda item: (not item["valid"], item["board_token"].casefold()))
    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "search_queries": list(queries),
        "successful_queries": successful_queries,
        "failed_queries": search_errors,
        "candidate_boards_found": len(candidates),
        "validated_boards_found": sum(1 for board in boards if board["valid"]),
        "boards": boards,
        "limitations": [
            "Discovery is limited to public search results and is not an exhaustive list of Greenhouse customers.",
            "A valid public board proves the feed is accessible, not that every job is relevant to a target region.",
            "Search engines may rate-limit requests or change indexing; rerun periodically to discover newly indexed boards.",
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
        ]
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for board in report.get("boards", []):
            if not board.get("valid"):
                continue
            writer.writerow({
                key: json.dumps(board.get(key), ensure_ascii=False)
                if key == "candidate_urls" else board.get(key, "")
                for key in fields
            })
    return json_path, csv_path
