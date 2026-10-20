"""CSV export helpers for manual review."""
import csv, json
from pathlib import Path
from typing import Any


def export_results_csv(results: list[dict[str, Any]], output_path: str | Path) -> Path:
    path = Path(output_path); path.parent.mkdir(parents=True, exist_ok=True)
    columns = ["supplied_url", "http_status", "final_url", "reachable", "page_title", "meta_description", "headings", "careers_links", "application_links", "classification", "evidence", "error"]
    with path.open("w", newline="", encoding="utf-8-sig") as file:
        writer = csv.DictWriter(file, fieldnames=columns, extrasaction="ignore"); writer.writeheader()
        for row in results:
            flattened = dict(row)
            for key in ("headings", "careers_links", "application_links", "evidence"):
                if isinstance(flattened.get(key), (list, dict)): flattened[key] = json.dumps(flattened[key], ensure_ascii=False)
            writer.writerow(flattened)
    return path
