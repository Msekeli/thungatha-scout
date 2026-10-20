"""Evidence-based investigation of a user-supplied careers URL.

This module does not discover URLs. It inspects the supplied page and only tries
public ATS endpoints when the page provides enough evidence to identify them.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

USER_AGENT = (
    "Mozilla/5.0 (compatible; ThungathaScout/0.2; "
    "+https://github.com/Msekeli/thungatha-scout)"
)
TIMEOUT = 20.0
MAX_JOBS = 100


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _workday_config(html: str, final_url: str) -> dict[str, str] | None:
    """Read Workday tenant/site/host only from visible page configuration or URL."""
    parsed = urlparse(final_url)
    host = parsed.netloc.lower()
    if "myworkdayjobs.com" not in host and "window.workday" not in html.lower():
        return None

    tenant_match = re.search(r'\btenant\s*:\s*["\']([^"\']+)["\']', html, re.I)
    site_match = re.search(r'\bsiteId\s*:\s*["\']([^"\']+)["\']', html, re.I)
    tenant = tenant_match.group(1) if tenant_match else host.split(".")[0]
    site = site_match.group(1) if site_match else ""
    if not tenant or not site or "myworkdayjobs.com" not in host:
        return {"host": host, "tenant": tenant, "site": site, "status": "incomplete_config"}
    return {"host": host, "tenant": tenant, "site": site, "status": "identified"}


def _greenhouse_board(html: str, final_url: str) -> str | None:
    """Find a Greenhouse board token only where page evidence exposes it."""
    candidates = re.findall(
        r"(?:boards-api\.greenhouse\.io/v1/boards/|boards\.greenhouse\.io/)([A-Za-z0-9_-]+)",
        html,
        re.I,
    )
    if candidates:
        return candidates[0]
    host = urlparse(final_url).netloc.lower()
    if "boards.greenhouse.io" in host:
        path_parts = [part for part in urlparse(final_url).path.split("/") if part]
        if path_parts:
            return path_parts[0]
    return None


def _detect_ats(html: str, final_url: str, links: list[dict[str, str]]) -> list[str]:
    evidence_text = " ".join([html[:1_500_000], final_url] + [x["url"] for x in links]).lower()
    ats: list[str] = []
    if "greenhouse.io" in evidence_text or "greenhouse" in evidence_text:
        ats.append("greenhouse")
    if "myworkdayjobs.com" in evidence_text or "window.workday" in evidence_text:
        ats.append("workday")
    for name, hints in {
        "lever": ("jobs.lever.co", "api.lever.co"),
        "smartrecruiters": ("jobs.smartrecruiters.com",),
        "workable": ("apply.workable.com",),
        "ashby": ("jobs.ashbyhq.com",),
        "successfactors": ("successfactors.com",),
        "teamtailor": ("teamtailor.com",),
    }.items():
        if any(hint in evidence_text for hint in hints):
            ats.append(name)
    return _unique(ats)


def _normalise_job(job: dict[str, Any], source: str) -> dict[str, Any]:
    location = job.get("location")
    if isinstance(location, dict):
        location_text = location.get("name") or location.get("label") or ""
    elif isinstance(location, list):
        location_text = ", ".join(
            str(item.get("name") or item.get("label") or item) if isinstance(item, dict) else str(item)
            for item in location
        )
    else:
        location_text = str(location or job.get("locationsText") or job.get("locationName") or "")
    departments = job.get("departments") or job.get("department") or []
    if isinstance(departments, list):
        department_text = ", ".join(
            str(item.get("name") or item.get("label") or item) if isinstance(item, dict) else str(item)
            for item in departments
        )
    elif isinstance(departments, dict):
        department_text = str(departments.get("name") or departments.get("label") or "")
    else:
        department_text = str(departments)
    job_url = job.get("absolute_url") or job.get("externalPath") or job.get("url") or job.get("externalUrl") or ""
    title = job.get("title") or job.get("name") or ""
    description = job.get("content") or job.get("description") or ""
    if isinstance(description, dict):
        description = description.get("text") or description.get("html") or ""
    return {
        "title": str(title).strip(),
        "location": location_text.strip(),
        "department": department_text.strip(),
        "url": str(job_url).strip(),
        "description_available": bool(str(description).strip()),
        "source_adapter": source,
    }


def _extract_greenhouse(client: httpx.Client, board: str) -> dict[str, Any]:
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    response = client.get(endpoint)
    result: dict[str, Any] = {
        "adapter": "greenhouse_public_board_api",
        "endpoint": endpoint,
        "http_status": response.status_code,
        "success": False,
        "jobs": [],
        "error": "",
    }
    if not response.is_success:
        result["error"] = f"Endpoint returned HTTP {response.status_code}"
        return result
    try:
        payload = response.json()
    except ValueError:
        result["error"] = "Endpoint did not return valid JSON"
        return result
    jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
    result["jobs"] = [
        _normalise_job(job, "greenhouse")
        for job in jobs[:MAX_JOBS]
        if isinstance(job, dict)
    ]
    result["total_jobs_reported"] = len(jobs)
    result["success"] = True
    return result


def _extract_workday(client: httpx.Client, config: dict[str, str]) -> dict[str, Any]:
    """Try Workday's public CXS jobs endpoint for an identified tenant/site."""
    host = config["host"]
    tenant = config["tenant"]
    site = config["site"]
    endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    result: dict[str, Any] = {
        "adapter": "workday_public_cxs_jobs",
        "endpoint": endpoint,
        "http_status": None,
        "success": False,
        "jobs": [],
        "error": "",
    }
    if config.get("status") != "identified":
        result["error"] = "Workday detected, but tenant/site configuration was incomplete; no endpoint request made."
        return result
    payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": ""}
    try:
        response = client.post(endpoint, json=payload, headers={"Accept": "application/json"})
        result["http_status"] = response.status_code
        if not response.is_success:
            result["error"] = f"Endpoint returned HTTP {response.status_code}"
            return result
        data = response.json()
        postings = data.get("jobPostings", []) if isinstance(data, dict) else []
        result["jobs"] = [
            _normalise_job(job, "workday")
            for job in postings[:MAX_JOBS]
            if isinstance(job, dict)
        ]
        result["total_jobs_reported"] = data.get("total", len(postings)) if isinstance(data, dict) else len(postings)
        result["success"] = True
        result["pagination"] = {
            "limit": payload["limit"],
            "offset": payload["offset"],
            "note": "First page only; pagination is not yet implemented.",
        }
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def investigate_careers_url(url: str, *, timeout: float = TIMEOUT) -> dict[str, Any]:
    """Inspect one supplied URL, detect ATS evidence, and try supported public adapters."""
    if not url.startswith(("https://", "http://")):
        raise ValueError("URL must begin with http:// or https://")

    report: dict[str, Any] = {
        "supplied_url": url,
        "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": None,
        "final_url": "",
        "content_type": "",
        "response_bytes": 0,
        "page_title": "",
        "page_text_excerpt": "",
        "ats_detected": [],
        "ats_evidence": [],
        "job_extraction": {
            "attempted": False,
            "success": False,
            "jobs": [],
            "adapters": [],
            "note": "",
        },
        "errors": [],
    }

    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=timeout,
            headers={"User-Agent": USER_AGENT},
        ) as client:
            response = client.get(url)
            report["http_status"] = response.status_code
            report["final_url"] = str(response.url)
            report["content_type"] = response.headers.get("content-type", "")
            report["response_bytes"] = len(response.content)
            if not response.is_success:
                report["errors"].append(f"Careers page returned HTTP {response.status_code}.")
                return report
            if "html" not in report["content_type"].lower():
                report["errors"].append("Careers URL did not return HTML.")
                return report

            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            title = soup.find("title")
            report["page_title"] = title.get_text(" ", strip=True) if title else ""
            for node in soup(["script", "style", "noscript", "svg"]):
                node.decompose()
            report["page_text_excerpt"] = soup.get_text(" ", strip=True)[:1200]

            links: list[dict[str, str]] = []
            for anchor in soup.find_all("a", href=True):
                link_url = urljoin(str(response.url), str(anchor["href"]).strip())
                if urlparse(link_url).scheme in ("http", "https"):
                    links.append({"label": anchor.get_text(" ", strip=True), "url": link_url})

            ats = _detect_ats(html, str(response.url), links)
            report["ats_detected"] = ats
            if "greenhouse" in ats:
                board = _greenhouse_board(html, str(response.url))
                if board:
                    report["ats_evidence"].append(
                        f"Greenhouse board token '{board}' found in supplied page HTML/URL."
                    )
                else:
                    report["ats_evidence"].append("Greenhouse references found, but no board token was extracted.")
            if "workday" in ats:
                config = _workday_config(html, str(response.url))
                # A corporate careers page may only link to Workday. Fetch that
                # observed link (never a guessed tenant URL) to read its config.
                if config is None:
                    workday_links = [
                        item["url"] for item in links
                        if "myworkdayjobs.com" in urlparse(item["url"]).netloc.lower()
                    ]
                    if workday_links:
                        try:
                            workday_response = client.get(workday_links[0])
                            if workday_response.is_success and "html" in workday_response.headers.get("content-type", "").lower():
                                config = _workday_config(workday_response.text, str(workday_response.url))
                                report["workday_landing_url"] = str(workday_response.url)
                            else:
                                report["errors"].append(
                                    f"Observed Workday link returned HTTP {workday_response.status_code} or non-HTML content."
                                )
                        except httpx.HTTPError as exc:
                            report["errors"].append(f"Could not inspect observed Workday link: {exc}")
                report["workday_config"] = config
                report["ats_evidence"].append(
                    "Workday references found in the careers page or its links."
                )
            else:
                config = None

            extraction = report["job_extraction"]
            extraction["attempted"] = True
            with httpx.Client(
                follow_redirects=True,
                timeout=timeout,
                headers={"User-Agent": USER_AGENT, "Accept": "application/json"},
            ) as api_client:
                if "greenhouse" in ats:
                    board = _greenhouse_board(html, str(response.url))
                    if board:
                        adapter_result = _extract_greenhouse(api_client, board)
                        extraction["adapters"].append(adapter_result)
                        if adapter_result["success"]:
                            extraction["jobs"].extend(adapter_result["jobs"])
                    else:
                        extraction["adapters"].append({
                            "adapter": "greenhouse_public_board_api",
                            "success": False,
                            "jobs": [],
                            "error": "No board token found; no guessed endpoint request made.",
                        })
                if "workday" in ats and config:
                    adapter_result = _extract_workday(api_client, config)
                    extraction["adapters"].append(adapter_result)
                    if adapter_result["success"]:
                        extraction["jobs"].extend(adapter_result["jobs"])

            extraction["success"] = any(adapter.get("success") for adapter in extraction["adapters"])
            if extraction["success"]:
                extraction["note"] = (
                    "At least one recognised public ATS endpoint returned structured data. "
                    "Job counts and descriptions still need validation."
                )
            elif ats:
                extraction["note"] = (
                    "ATS detected, but supported endpoint extraction did not return structured jobs. "
                    "Review adapter errors; ATS detection alone is not extraction success."
                )
            else:
                extraction["note"] = (
                    "No supported ATS detected. Ordinary HTML inspection completed; "
                    "no browser automation or blind endpoint probing was attempted."
                )
    except (httpx.HTTPError, ValueError) as exc:
        report["errors"].append(str(exc))
    return report


def save_investigation_report(report: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    """Write separate JSON and Markdown reports; never modifies companies.csv."""
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    parsed = urlparse(str(report.get("supplied_url", "")))
    slug = re.sub(r"[^a-z0-9]+", "-", (parsed.netloc + parsed.path).lower()).strip("-") or "careers-url"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    base = out_dir / f"{slug[:90]}-{stamp}"
    json_path = base.with_suffix(".json")
    markdown_path = base.with_suffix(".md")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    extraction = report.get("job_extraction", {})
    jobs = extraction.get("jobs", []) if isinstance(extraction, dict) else []
    lines = [
        "# Careers URL Investigation",
        "",
        f"- Supplied URL: {report.get('supplied_url', '')}",
        f"- Final URL: {report.get('final_url', '')}",
        f"- HTTP status: {report.get('http_status', '')}",
        f"- Page title: {report.get('page_title', '')}",
        f"- ATS detected: {', '.join(report.get('ats_detected', [])) or 'none detected'}",
        f"- Extraction success: {bool(extraction.get('success', False))}",
        f"- Jobs extracted in this response: {len(jobs)}",
        "",
        "## Assessment",
        "",
        str(extraction.get("note", "")),
        "",
        "## ATS evidence",
        "",
    ]
    lines.extend([f"- {item}" for item in report.get("ats_evidence", [])] or ["- No ATS evidence recorded."])
    lines.extend(["", "## Adapter results", ""])
    adapters = extraction.get("adapters", [])
    if adapters:
        for adapter in adapters:
            lines.append(f"- **{adapter.get('adapter', 'unknown')}**: success={adapter.get('success', False)}; HTTP={adapter.get('http_status', 'n/a')}; reported jobs={adapter.get('total_jobs_reported', 'n/a')}; error={adapter.get('error', '')}")
    else:
        lines.append("- No ATS adapter was attempted.")
    lines.extend(["", "## Extracted jobs", ""])
    if jobs:
        for job in jobs:
            lines.append(f"- **{job.get('title') or '(untitled)'}** — {job.get('location') or 'location not provided'}")
            if job.get("url"):
                lines.append(f"  - {job['url']}")
            lines.append(f"  - Description present in response: {job.get('description_available', False)}")
    else:
        lines.append("- No jobs were extracted.")
    if report.get("errors"):
        lines.extend(["", "## Errors", ""])
        lines.extend([f"- {error}" for error in report["errors"]])
    lines.extend(["", "## Limitations", "", "- This report reflects one inspection run, not a guarantee of completeness or long-term endpoint stability.", "- Only the first page of Workday results is currently requested.", "- No application forms are submitted and no account-protected content is accessed.", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path
