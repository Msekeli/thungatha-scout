"""Rank Greenhouse vacancies by target geography and software-role relevance."""
from __future__ import annotations

import csv
import json
import re
from pathlib import Path
from typing import Any

SOUTH_AFRICA_TERMS = (
    "south africa", "cape town", "johannesburg", "pretoria", "durban",
    "stellenbosch", "western cape", "gauteng", "south african",
)
REMOTE_TERMS = ("remote", "anywhere", "distributed")
ROLE_TERMS = (
    "software", "developer", "engineer", "frontend", "front-end", "backend",
    "back-end", "full stack", "full-stack", "web", "platform", "devops",
    "cloud", "data engineer", "machine learning", "ai engineer", "qa engineer",
    "quality assurance", "site reliability", "solutions architect",
)
NON_ROLE_TERMS = (
    "account executive", "sales", "recruiter", "human resources", "customer success",
    "marketing", "legal counsel", "warehouse", "driver", "nurse",
)


def classify_job(job: dict[str, Any], board_token: str = "") -> dict[str, Any]:
    title = str(job.get("title") or "").strip()
    location = str(job.get("location") or "").strip()
    department = str(job.get("department") or "").strip()
    haystack = f"{title} {department}".casefold()
    location_text = location.casefold()
    south_africa = any(term in location_text for term in SOUTH_AFRICA_TERMS)
    remote = any(term in location_text for term in REMOTE_TERMS)
    role_matches = [term for term in ROLE_TERMS if term in haystack]
    non_role_matches = [term for term in NON_ROLE_TERMS if term in haystack]
    role_relevant = bool(role_matches) and not (non_role_matches and not any(
        term in haystack for term in ("software", "developer", "engineer", "devops", "data engineer")
    ))
    score = (100 if south_africa else 35 if remote else 0) + (30 if role_relevant else 0)
    if south_africa and remote:
        score += 5
    if not location:
        geography = "unknown"
    elif south_africa:
        geography = "south_africa"
    elif remote:
        geography = "remote_unspecified"
    else:
        geography = "other_location"
    return {
        "board_token": board_token,
        "title": title,
        "location": location,
        "department": department,
        "url": str(job.get("url") or "").strip(),
        "source_adapter": str(job.get("source_adapter") or "greenhouse"),
        "geography": geography,
        "role_relevant": role_relevant,
        "role_matches": ", ".join(role_matches),
        "relevance_score": score,
        "review_reason": (
            "South African location and software/engineering role"
            if south_africa and role_relevant else
            "Remote-labelled software/engineering role; confirm eligible countries"
            if remote and role_relevant else
            "Location not stated; manual review needed"
            if not location else
            "Does not match target geography and role filters"
        ),
    }


def analyze_greenhouse_report(report_path: str | Path, output_dir: str | Path) -> dict[str, Any]:
    source = Path(report_path)
    report = json.loads(source.read_text(encoding="utf-8"))
    ranked: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    for board in report.get("boards", []):
        if not board.get("valid"):
            continue
        token = str(board.get("board_token") or "")
        for job in board.get("jobs", []):
            if not isinstance(job, dict):
                continue
            item = classify_job(job, token)
            url = item["url"].split("#", 1)[0].rstrip("/")
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            ranked.append(item)
    ranked.sort(key=lambda item: (-item["relevance_score"], item["board_token"].casefold(), item["title"].casefold()))

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / "greenhouse-job-relevance.json"
    csv_path = out / "greenhouse-job-relevance.csv"
    json_path.write_text(json.dumps({
        "source_report": str(source),
        "unique_jobs_reviewed": len(ranked),
        "south_africa_software_jobs": sum(1 for x in ranked if x["geography"] == "south_africa" and x["role_relevant"]),
        "remote_software_jobs_country_unconfirmed": sum(1 for x in ranked if x["geography"] == "remote_unspecified" and x["role_relevant"]),
        "unknown_location_software_jobs": sum(1 for x in ranked if x["geography"] == "unknown" and x["role_relevant"]),
        "jobs": ranked,
        "limitations": [
            "Location and role relevance are heuristic matches against the fields in the saved report.",
            "Remote does not prove that South African applicants are eligible; confirm the vacancy page.",
            "Jobs without location data are retained for manual review but are not counted as South African matches.",
            "Deduplication uses normalized vacancy URL only; cross-board duplicates with different URLs may remain.",
        ],
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    fields = [
        "board_token", "title", "location", "department", "url", "source_adapter",
        "geography", "role_relevant", "role_matches", "relevance_score", "review_reason",
    ]
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(ranked)
    return {
        "source_report": str(source),
        "unique_jobs_reviewed": len(ranked),
        "south_africa_software_jobs": sum(1 for x in ranked if x["geography"] == "south_africa" and x["role_relevant"]),
        "remote_software_jobs_country_unconfirmed": sum(1 for x in ranked if x["geography"] == "remote_unspecified" and x["role_relevant"]),
        "unknown_location_software_jobs": sum(1 for x in ranked if x["geography"] == "unknown" and x["role_relevant"]),
        "json_report": str(json_path),
        "csv_report": str(csv_path),
        "top_matches": [x for x in ranked if x["relevance_score"] >= 130][:20],
    }
