"""Small HTTP API for validating Greenhouse and Workday job feeds in Postman.

The first release intentionally supports Cape Town only. Source adapters return
provider data; this module maps it to one source-neutral response contract.
"""
from __future__ import annotations

import re
import time
from typing import Any

import httpx
from fastapi import FastAPI, HTTPException, Query

from app.workday import (
    WorkdayError,
    fetch_job_detail,
    fetch_jobs as fetch_workday_jobs,
    parse_board_url,
)

app = FastAPI(title="Thungatha Scout Jobs API", version="0.1.0")

GREENHOUSE_BOARD_TOKEN = re.compile(r"^[A-Za-z0-9_-]{1,100}$")
CAPE_TOWN = "cape town"


def _is_cape_town(job: dict[str, Any]) -> bool:
    """Match Cape Town explicitly; do not treat all Western Cape locations as local."""
    locations = [job.get("location") or ""]
    locations.extend(job.get("additional_locations") or [])
    return any(CAPE_TOWN in str(location).casefold() for location in locations)


def _normalize_greenhouse_job(
    board: str, item: dict[str, Any], company_name: str | None = None
) -> dict[str, Any]:
    location_value = item.get("location")
    if isinstance(location_value, dict):
        location = location_value.get("name") or ""
    else:
        location = str(location_value or "")

    departments = item.get("departments") or []
    department_names = [
        str(entry.get("name") or "")
        for entry in departments
        if isinstance(entry, dict) and entry.get("name")
    ]
    url = str(item.get("absolute_url") or "")
    description = str(item.get("content") or "")

    return {
        "source_type": "greenhouse",
        "company_name": company_name,
        "company_key": board,
        "source_id": str(item.get("id") or ""),
        "title": str(item.get("title") or "").strip(),
        "location": location.strip(),
        "additional_locations": [],
        "department": ", ".join(department_names),
        "employment_type": None,
        "posted_at": None,
        "closing_at": None,
        "description_html": description or None,
        "job_url": url,
        "application_url": url,
        "status": "active",
        "board_url": f"https://job-boards.greenhouse.io/{board}",
    }


def _normalize_workday_job(
    careers_url: str, item: dict[str, Any], company_name: str | None = None
) -> dict[str, Any]:
    board = parse_board_url(careers_url)
    external_path = str(item.get("external_path") or "")
    prefix = f"/{board.locale}/" if board.locale else "/"
    canonical_url = (
        f"{board.origin}{prefix}{board.site}{external_path}"
        if external_path.startswith("/") and not external_path.startswith("//")
        else str(item.get("url") or "")
    )
    application_url = str(item.get("url") or canonical_url)

    return {
        "source_type": "workday",
        "company_name": company_name,
        "company_key": board.tenant,
        "source_id": str(item.get("source_id") or ""),
        "title": str(item.get("title") or "").strip(),
        "location": str(item.get("location") or "").strip(),
        "additional_locations": item.get("additional_locations") or [],
        "department": None,
        "employment_type": item.get("employment_type"),
        "posted_at": None,
        "closing_at": None,
        "description_html": item.get("description_html"),
        "job_url": canonical_url,
        "application_url": application_url,
        "status": "active",
        "board_url": board.careers_url,
    }


def _fetch_greenhouse(
    board: str, *, max_jobs: int, company_name: str | None = None
) -> list[dict[str, Any]]:
    if not GREENHOUSE_BOARD_TOKEN.fullmatch(board):
        raise ValueError("Board must be a Greenhouse board token, not an arbitrary URL.")

    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    try:
        with httpx.Client(timeout=20.0, follow_redirects=True) as client:
            response = client.get(endpoint, headers={"Accept": "application/json"})
            response.raise_for_status()
            payload = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise RuntimeError(f"Could not read Greenhouse board '{board}': {exc}") from exc

    if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
        raise RuntimeError("Greenhouse returned an unexpected jobs response.")

    normalized = [
        _normalize_greenhouse_job(board, item, company_name)
        for item in payload["jobs"]
        if isinstance(item, dict)
    ]
    # Filter by location before applying the result cap; Cape Town jobs may not
    # appear near the beginning of a company's board.
    return normalized


def _response(
    source: str, jobs: list[dict[str, Any]], fetched_count: int, max_jobs: int
) -> dict[str, Any]:
    local_jobs = [job for job in jobs if _is_cape_town(job)][:max_jobs]
    return {
        "source_type": source,
        "location_scope": "Cape Town, South Africa",
        "fetched_count": fetched_count,
        "returned_count": len(local_jobs),
        "jobs": local_jobs,
    }


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "healthy"}


@app.get("/api/jobs/greenhouse")
def greenhouse_jobs(
    board: str = Query(..., description="Greenhouse board token, e.g. ozow"),
    company_name: str | None = Query(default=None, description="Verified employer display name"),
    max_jobs: int = Query(default=100, ge=1, le=500),
) -> dict[str, Any]:
    try:
        jobs = _fetch_greenhouse(board, max_jobs=max_jobs, company_name=company_name)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _response("greenhouse", jobs, len(jobs), max_jobs)


@app.get("/api/jobs/workday")
def workday_jobs(
    careers_url: str = Query(..., description="Official public Workday careers-board URL"),
    company_name: str | None = Query(default=None, description="Verified employer display name"),
    max_jobs: int = Query(default=40, ge=1, le=200),
    include_details: bool = Query(default=False),
) -> dict[str, Any]:
    try:
        # Scan list records first, then fetch expensive details only for the
        # Cape Town results we intend to return.
        jobs = fetch_workday_jobs(
            careers_url,
            max_jobs=200,
            include_details=False,
            request_delay_seconds=0.1,
        )
        normalized = [_normalize_workday_job(careers_url, job, company_name) for job in jobs]
        local_jobs = [job for job in normalized if _is_cape_town(job)][:max_jobs]

        if include_details and local_jobs:
            board = parse_board_url(careers_url)
            with httpx.Client(follow_redirects=True, timeout=20.0) as detail_client:
                for index, job in enumerate(local_jobs):
                    external_path = next(
                        (item.get("external_path") for item in jobs
                         if str(item.get("source_id") or "") == job["source_id"]),
                        "",
                    )
                    if not external_path:
                        continue
                    detail = fetch_job_detail(detail_client, board, str(external_path))
                    job["title"] = str(detail.get("title") or job["title"])
                    job["location"] = str(detail.get("location") or job["location"])
                    additional = detail.get("additionalLocations") or []
                    if isinstance(additional, list):
                        job["additional_locations"] = [
                            str(item.get("descriptor") or "")
                            for item in additional if isinstance(item, dict)
                        ]
                    job["description_html"] = detail.get("jobDescription")
                    job["employment_type"] = detail.get("timeType") or job["employment_type"]
                    external_url = detail.get("externalUrl")
                    if external_url:
                        job["application_url"] = str(external_url)
                    if index < len(local_jobs) - 1:
                        time.sleep(0.1)
        normalized = local_jobs
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except (WorkdayError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    return _response("workday", normalized, len(normalized), max_jobs)
