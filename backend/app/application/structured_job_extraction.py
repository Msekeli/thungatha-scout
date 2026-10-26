"""Extract Schema.org JobPosting records from already-retrieved HTML."""
from __future__ import annotations

import json
import re
from typing import Any
from urllib.parse import urljoin, urlsplit

_SCRIPT_RE = re.compile(
    r"<script\b(?=[^>]*\btype\s*=\s*['\"]application/ld\+json['\"])[^>]*>(.*?)</script\s*>",
    re.IGNORECASE | re.DOTALL,
)


def _objects(value: Any):
    """Yield JSON objects recursively, including objects inside @graph and arrays."""
    if isinstance(value, list):
        for item in value:
            yield from _objects(item)
    elif isinstance(value, dict):
        yield value
        for key, child in value.items():
            if key in {"@graph", "mainEntity", "itemListElement"}:
                yield from _objects(child)


def _is_job_posting(item: dict[str, Any]) -> bool:
    kind = item.get("@type", [])
    kinds = kind if isinstance(kind, list) else [kind]
    return any(str(value).rsplit("/", 1)[-1] == "JobPosting" for value in kinds)


def _text(value: Any) -> str:
    if isinstance(value, dict):
        value = value.get("name") or value.get("value") or ""
    if isinstance(value, list):
        return ", ".join(filter(None, (_text(item) for item in value)))
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _locations(value: Any) -> list[str]:
    entries = value if isinstance(value, list) else [value]
    found = []
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        address = entry.get("address", entry)
        if not isinstance(address, dict):
            continue
        parts = [_text(address.get(key)) for key in (
            "addressLocality", "addressRegion", "addressCountry"
        )]
        location = ", ".join(part for part in parts if part)
        if location and location not in found:
            found.append(location)
    return found


def extract_job_postings(html: str, page_url: str, company_name: str) -> list[dict[str, Any]]:
    """Return validated JobPosting candidates; malformed JSON-LD is ignored safely."""
    results: list[dict[str, Any]] = []
    seen: set[str] = set()
    for match in _SCRIPT_RE.finditer(html):
        try:
            payload = json.loads(match.group(1).strip())
        except (json.JSONDecodeError, TypeError):
            continue
        for item in _objects(payload):
            if not _is_job_posting(item):
                continue
            title = _text(item.get("title"))
            raw_url = item.get("url") or item.get("mainEntityOfPage") or page_url
            if isinstance(raw_url, dict):
                raw_url = raw_url.get("@id") or raw_url.get("url") or ""
            job_url = urljoin(page_url, str(raw_url))
            parsed = urlsplit(job_url)
            if not title or parsed.scheme not in {"http", "https"} or not parsed.netloc:
                continue
            if job_url in seen:
                continue
            seen.add(job_url)
            results.append({
                "company": company_name,
                "title": title,
                "job_url": job_url,
                "description": _text(item.get("description")),
                "date_posted": _text(item.get("datePosted")),
                "valid_through": _text(item.get("validThrough")),
                "employment_type": _text(item.get("employmentType")),
                "locations": _locations(item.get("jobLocation")),
                "source_type": "schema_job_posting",
                "source_page_url": page_url,
                "evidence": "Schema.org JobPosting JSON-LD",
            })
    return results
