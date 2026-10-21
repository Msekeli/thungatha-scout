"""Export all vacancies already captured in a Greenhouse discovery report.

This stage does not filter by role or geography. It preserves company/board
provenance and adds simple location flags so downstream workflows can filter.
"""
from __future__ import annotations

import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


WESTERN_CAPE_TERMS = ("cape town", "western cape", "stellenbosch", "paarl", "george", "durbanville")
SOUTH_AFRICA_TERMS = (
    "south africa", "cape town", "johannesburg", "pretoria", "durban",
    "stellenbosch", "western cape", "gauteng", "paarl", "george", "south african",
)


def _location_flags(location: str) -> tuple[str, str]:
    value = location.casefold()
    if not value:
        return "unknown", "unknown"
    south_africa = any(term in value for term in SOUTH_AFRICA_TERMS)
    western_cape = any(term in value for term in WESTERN_CAPE_TERMS)
    return (
        "yes" if western_cape else "no",
        "yes" if south_africa else "no",
    )


def extract_greenhouse_jobs(report_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    """Export every usable job record in a saved discovery report without role filters."""
    source = Path(report_path)
    report = json.loads(source.read_text(encoding="utf-8"))
    extracted_at = datetime.now(timezone.utc).isoformat()
    jobs: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    boards_seen = 0
    boards_with_jobs = 0

    for board in report.get("boards", []):
        boards_seen += 1
        board_jobs = board.get("jobs", [])
        if board_jobs:
            boards_with_jobs += 1
        token = str(board.get("board_token") or "")
        company_name = str(board.get("company_name") or "").strip()
        candidates = board.get("company_name_candidates") or []
        company_label = company_name or (", ".join(str(x) for x in candidates if x) or "Unresolved employer")
        for job in board_jobs:
            if not isinstance(job, dict):
                continue
            title = str(job.get("title") or "").strip()
            url = str(job.get("url") or "").strip()
            if not title or not url.startswith(("https://", "http://")):
                continue
            dedupe_key = re.sub(r"/+$", "", url.split("#", 1)[0]).casefold()
            if not dedupe_key or dedupe_key in seen_urls:
                continue
            seen_urls.add(dedupe_key)
            location = str(job.get("location") or "").strip()
            western_cape, south_africa = _location_flags(location)
            jobs.append({
                "company_name": company_label,
                "company_identity_status": str(board.get("company_identity_status") or "unresolved_board_identity"),
                "company_name_candidates": " | ".join(str(x) for x in candidates if x),
                "board_token": token,
                "board_url": str(board.get("board_url") or f"https://job-boards.greenhouse.io/{token}"),
                "board_api_status": "accessible" if board.get("board_exists") or board.get("valid") else "not_verified",
                "job_id": str(job.get("id") or ""),
                "title": title,
                "location": location,
                "department": str(job.get("department") or "").strip(),
                "url": url,
                "source_adapter": str(job.get("source_adapter") or "greenhouse"),
                "description_available": bool(job.get("description_available", False)),
                "western_cape_location_match": western_cape,
                "south_africa_location_match": south_africa,
                "extracted_at_utc": extracted_at,
            })

    jobs.sort(key=lambda item: (
        item["western_cape_location_match"] != "yes",
        item["south_africa_location_match"] != "yes",
        item["company_name"].casefold(),
        item["title"].casefold(),
    ))
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "greenhouse-jobs.json"
    csv_path = out / "greenhouse-jobs.csv"
    summary = {
        "source_report": str(source),
        "extracted_at_utc": extracted_at,
        "boards_in_source_report": boards_seen,
        "boards_with_jobs": boards_with_jobs,
        "unique_jobs_extracted": len(jobs),
        "western_cape_location_matches": sum(job["western_cape_location_match"] == "yes" for job in jobs),
        "south_africa_location_matches": sum(job["south_africa_location_match"] == "yes" for job in jobs),
        "unknown_location_jobs": sum(job["western_cape_location_match"] == "unknown" for job in jobs),
        "jobs": jobs,
        "limitations": [
            "Exports only the jobs captured in the supplied discovery report; it does not refresh board APIs.",
            "No job-title, industry, or location filter is applied; location flags are simple text matches.",
            "A job with a remote or ambiguous location may require checking the original vacancy page.",
            "Company identity labels preserve unresolved candidates instead of treating board tokens as company names.",
            "Deduplication uses the vacancy URL after removing fragments and trailing slashes.",
        ],
    }
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = [
        "company_name", "company_identity_status", "company_name_candidates",
        "board_token", "board_url", "board_api_status", "job_id", "title",
        "location", "department", "url", "source_adapter", "description_available",
        "western_cape_location_match", "south_africa_location_match", "extracted_at_utc",
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(jobs)
    return {
        "source_report": str(source),
        "boards_in_source_report": boards_seen,
        "boards_with_jobs": boards_with_jobs,
        "unique_jobs_extracted": len(jobs),
        "western_cape_location_matches": summary["western_cape_location_matches"],
        "south_africa_location_matches": summary["south_africa_location_matches"],
        "unknown_location_jobs": summary["unknown_location_jobs"],
        "json_report": str(json_path),
        "csv_report": str(csv_path),
    }
