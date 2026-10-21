"""Client for public Workday Candidate Experience (CXS) career boards.

This uses the same public JSON endpoints that Workday-hosted career pages use.
The CXS interface is undocumented, so callers should handle schema changes and
source-side rate limiting gracefully.
"""
from __future__ import annotations

import time
from dataclasses import asdict, dataclass
from typing import Any
from urllib.parse import urlparse

import httpx

PAGE_SIZE = 20
USER_AGENT = "ThungathaScout/0.1 (public careers-board integration)"


class WorkdayError(RuntimeError):
    """Raised when a Workday board cannot be read reliably."""


@dataclass(frozen=True)
class WorkdayBoard:
    careers_url: str
    origin: str
    tenant: str
    site: str
    locale: str | None = None

    @property
    def jobs_endpoint(self) -> str:
        return f"{self.origin}/wday/cxs/{self.tenant}/{self.site}/jobs"

    @property
    def details_prefix(self) -> str:
        return f"{self.origin}/wday/cxs/{self.tenant}/{self.site}"


def parse_board_url(url: str) -> WorkdayBoard:
    """Parse a public myworkdayjobs.com careers URL into its CXS identifiers."""
    parsed = urlparse(url.strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or not host.endswith(".myworkdayjobs.com"):
        raise ValueError("Expected a public https://<tenant>.wdN.myworkdayjobs.com/<site> URL.")

    host_parts = host.split(".")
    if len(host_parts) < 4 or not host_parts[0]:
        raise ValueError("Could not determine the Workday tenant from the careers URL.")

    path_parts = [part for part in parsed.path.split("/") if part]
    if not path_parts:
        raise ValueError("The Workday careers URL must include a site name.")

    locale = None
    if len(path_parts) > 1 and len(path_parts[0]) == 5 and path_parts[0][2] == "-":
        locale = path_parts.pop(0)

    if not path_parts:
        raise ValueError("The Workday careers URL must include a site name.")

    tenant = host_parts[0]
    site = path_parts[0]  # Site identifier is case-sensitive.
    origin = f"https://{parsed.netloc}"
    clean_url = f"{origin}/" + (f"{locale}/" if locale else "") + site
    return WorkdayBoard(clean_url, origin, tenant, site, locale)


def _headers(board: WorkdayBoard) -> dict[str, str]:
    return {
        "User-Agent": USER_AGENT,
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Referer": board.careers_url,
        "Origin": board.origin,
    }


def _json_or_error(response: httpx.Response, context: str) -> dict[str, Any]:
    if response.status_code in {403, 429}:
        raise WorkdayError(
            f"Workday returned HTTP {response.status_code} for {context}; "
            "the source may be restricting requests. Retry later; do not treat this as zero jobs."
        )
    try:
        response.raise_for_status()
        payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise WorkdayError(f"Could not read Workday {context}: {exc}") from exc
    if not isinstance(payload, dict):
        raise WorkdayError(f"Workday {context} returned an unexpected response shape.")
    return payload


def fetch_job_page(
    client: httpx.Client, board: WorkdayBoard, offset: int = 0
) -> dict[str, Any]:
    """Fetch one page. Workday's public CXS endpoint expects a page size of 20."""
    response = client.post(
        board.jobs_endpoint,
        headers=_headers(board),
        json={
            "appliedFacets": {},
            "limit": PAGE_SIZE,
            "offset": offset,
            "searchText": "",
        },
    )
    payload = _json_or_error(response, f"job list (offset {offset})")
    postings = payload.get("jobPostings")
    if not isinstance(postings, list):
        raise WorkdayError("Workday job-list response did not contain a jobPostings array.")
    return payload


def fetch_job_detail(
    client: httpx.Client, board: WorkdayBoard, external_path: str
) -> dict[str, Any]:
    """Fetch details for one listing path returned by the same Workday board."""
    if not external_path.startswith("/"):
        raise WorkdayError("Workday returned an invalid externalPath.")
    # Do not allow a source payload to redirect detail requests to another host.
    if "://" in external_path or external_path.startswith("//"):
        raise WorkdayError("Workday returned an unsafe externalPath.")
    response = client.get(
        f"{board.details_prefix}{external_path}",
        headers={**_headers(board), "Content-Type": "application/json"},
    )
    payload = _json_or_error(response, f"job detail ({external_path})")
    info = payload.get("jobPostingInfo")
    if not isinstance(info, dict):
        raise WorkdayError("Workday job-detail response did not contain jobPostingInfo.")
    return info


def normalize_job(board: WorkdayBoard, listing: dict[str, Any], detail: dict[str, Any] | None = None) -> dict[str, Any]:
    """Map Workday's list/detail shapes to a source-neutral vacancy record."""
    detail = detail or {}
    external_path = listing.get("externalPath") or ""
    locations = detail.get("additionalLocations") or []
    location = detail.get("location") or listing.get("locationsText")
    if isinstance(locations, list):
        additional_locations = [
            item.get("descriptor") if isinstance(item, dict) else str(item)
            for item in locations
        ]
    else:
        additional_locations = []

    apply_url = detail.get("externalUrl")
    if not apply_url and external_path:
        prefix = f"/{board.locale}/" if board.locale else "/"
        apply_url = f"{board.origin}{prefix}{board.site}{external_path}"

    bullet_fields = listing.get("bulletFields") or []
    req_id = detail.get("jobReqId")
    if not req_id and bullet_fields:
        req_id = str(bullet_fields[-1])

    return {
        "source_type": "workday",
        "company_key": board.tenant,
        "board_url": board.careers_url,
        "source_id": str(req_id or external_path.rsplit("_", 1)[-1] or external_path),
        "title": detail.get("title") or listing.get("title"),
        "location": location,
        "additional_locations": additional_locations,
        "posted_label": listing.get("postedOn"),
        "posted_at": detail.get("startDate"),
        "employment_type": detail.get("timeType"),
        "description_html": detail.get("jobDescription"),
        "url": apply_url,
        "external_path": external_path,
    }


def fetch_jobs(
    careers_url: str,
    *,
    max_jobs: int = 100,
    include_details: bool = False,
    request_delay_seconds: float = 0.25,
    timeout_seconds: float = 20.0,
    client: httpx.Client | None = None,
) -> list[dict[str, Any]]:
    """Fetch up to max_jobs from a public Workday board, with safe pagination."""
    if max_jobs < 1:
        raise ValueError("max_jobs must be at least 1.")
    board = parse_board_url(careers_url)
    owns_client = client is None
    session = client or httpx.Client(
        follow_redirects=True,
        timeout=timeout_seconds,
        headers={"User-Agent": USER_AGENT},
    )
    try:
        jobs: list[dict[str, Any]] = []
        offset = 0
        first_total: int | None = None
        seen_paths: set[str] = set()

        while len(jobs) < max_jobs:
            payload = fetch_job_page(session, board, offset)
            if first_total is None:
                total = payload.get("total")
                first_total = total if isinstance(total, int) and total >= 0 else None

            postings = payload["jobPostings"]
            if not postings:
                break

            for listing in postings:
                if not isinstance(listing, dict):
                    continue
                path = listing.get("externalPath") or ""
                if path and path in seen_paths:
                    continue
                if path:
                    seen_paths.add(path)
                detail = None
                if include_details and path:
                    if request_delay_seconds > 0:
                        time.sleep(request_delay_seconds)
                    detail = fetch_job_detail(session, board, path)
                jobs.append(normalize_job(board, listing, detail))
                if len(jobs) >= max_jobs:
                    break

            offset += PAGE_SIZE
            if first_total is not None and offset >= first_total:
                break
            if request_delay_seconds > 0 and len(jobs) < max_jobs:
                time.sleep(request_delay_seconds)

        return jobs
    finally:
        if owns_client:
            session.close()


def summarize_jobs(jobs: list[dict[str, Any]]) -> dict[str, Any]:
    """Return a small CLI-friendly summary without dumping job descriptions."""
    return {
        "jobs_returned": len(jobs),
        "jobs_with_location": sum(bool(job.get("location")) for job in jobs),
        "jobs_with_description": sum(bool(job.get("description_html")) for job in jobs),
        "sample": [
            {
                "title": job.get("title"),
                "location": job.get("location"),
                "url": job.get("url"),
                "source_id": job.get("source_id"),
            }
            for job in jobs[:5]
        ],
    }
