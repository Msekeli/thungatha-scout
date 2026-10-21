"""CSV export helpers for company-discovery and verification results."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any


def _export_csv(
    rows: list[dict[str, Any]],
    output_path: str | Path,
    columns: list[str],
) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            flattened = dict(row)
            for key, value in flattened.items():
                if isinstance(value, (list, dict)):
                    flattened[key] = json.dumps(value, ensure_ascii=False)
            writer.writerow(flattened)

    return path


def export_results_csv(
    results: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Export known-URL verification results."""
    return _export_csv(
        results,
        output_path,
        [
            "supplied_url",
            "http_status",
            "final_url",
            "reachable",
            "page_title",
            "meta_description",
            "headings",
            "careers_links",
            "application_links",
            "classification",
            "evidence",
            "error",
        ],
    )


def export_candidates_csv(
    candidates: list[dict[str, Any]],
    output_path: str | Path,
) -> Path:
    """Export discovered candidate companies for human review."""
    return _export_csv(
        candidates,
        output_path,
        [
            "name",
            "source_url",
            "snippet",
            "candidate_url",
            "region_hint",
            "role_hints",
            "employer_type",
            "official_website_url",
            "careers_url",
            "discovery_method",
            "evidence",
            "review_status",
        ],
    )
