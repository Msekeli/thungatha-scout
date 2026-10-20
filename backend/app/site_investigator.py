"""Evidence-based investigation of a user-supplied careers URL.

Only follows links observed on the supplied page, stays on the same corporate
host for generic vacancy extraction, and uses public ATS endpoints when the
page provides sufficient evidence. Never submits applications.
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

USER_AGENT = "Mozilla/5.0 (compatible; ThungathaScout/0.3; +https://github.com/Msekeli/thungatha-scout)"
TIMEOUT = 20.0
MAX_JOBS = 100
MAX_DETAIL_PAGES = 25


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value for value in values if value))


def _workday_config(html: str, final_url: str) -> dict[str, str] | None:
    """Read Workday tenant/site/host only from observed page configuration or URL."""
    parsed = urlparse(final_url)
    host = parsed.netloc.lower()
    if "myworkdayjobs.com" not in host and "window.workday" not in html.lower():
        return None
    tenant_match = re.search(r'\btenant\s*:\s*["\']([^"\']+)["\']', html, re.I)
    site_match = re.search(r'\bsiteId\s*:\s*["\']([^"\']+)["\']', html, re.I)
    tenant = tenant_match.group(1) if tenant_match else host.split(".")[0]
    site = site_match.group(1) if site_match else ""
    status = "identified" if tenant and site and "myworkdayjobs.com" in host else "incomplete_config"
    return {"host": host, "tenant": tenant, "site": site, "status": status}


def _greenhouse_board(html: str, final_url: str) -> str | None:
    candidates = re.findall(
        r"(?:boards-api\.greenhouse\.io/v1/boards/|boards\.greenhouse\.io/)([A-Za-z0-9_-]+)",
        html, re.I,
    )
    if candidates:
        return candidates[0]
    host = urlparse(final_url).netloc.lower()
    if "boards.greenhouse.io" in host:
        parts = [part for part in urlparse(final_url).path.split("/") if part]
        return parts[0] if parts else None
    return None


def _detect_ats(html: str, final_url: str, links: list[dict[str, str]]) -> list[str]:
    evidence = " ".join([html[:1_500_000], final_url] + [x["url"] for x in links]).lower()
    ats: list[str] = []
    if "greenhouse.io" in evidence:
        ats.append("greenhouse")
    if "myworkdayjobs.com" in evidence or "window.workday" in evidence:
        ats.append("workday")
    if "bamboohr.com" in evidence:
        ats.append("bamboohr")
    if "breezy.hr" in evidence:
        ats.append("breezyhr")
    for name, hints in {
        "lever": ("jobs.lever.co", "api.lever.co"),
        "smartrecruiters": ("jobs.smartrecruiters.com",),
        "workable": ("apply.workable.com",),
        "ashby": ("jobs.ashbyhq.com",),
        "successfactors": ("successfactors.com",),
        "teamtailor": ("teamtailor.com",),
    }.items():
        if any(hint in evidence for hint in hints):
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
    description = job.get("content") or job.get("description") or ""
    if isinstance(description, dict):
        description = description.get("text") or description.get("html") or ""
    return {
        "title": str(job.get("title") or job.get("name") or "").strip(),
        "location": location_text.strip(),
        "department": department_text.strip(),
        "url": str(job.get("absolute_url") or job.get("externalPath") or job.get("url") or job.get("externalUrl") or "").strip(),
        "description_available": bool(str(description).strip()),
        "source_adapter": source,
    }


def _extract_greenhouse(client: httpx.Client, board: str) -> dict[str, Any]:
    endpoint = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    result: dict[str, Any] = {"adapter": "greenhouse_public_board_api", "endpoint": endpoint,
                              "http_status": None, "success": False, "jobs": [], "error": ""}
    try:
        response = client.get(endpoint)
        result["http_status"] = response.status_code
        if not response.is_success:
            result["error"] = f"Endpoint returned HTTP {response.status_code}"
            return result
        payload = response.json()
        jobs = payload.get("jobs", []) if isinstance(payload, dict) else []
        result["jobs"] = [_normalise_job(job, "greenhouse") for job in jobs[:MAX_JOBS] if isinstance(job, dict)]
        result["total_jobs_reported"] = len(jobs)
        result["success"] = True
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def _extract_workday(client: httpx.Client, config: dict[str, str], *, search_text: str = "") -> dict[str, Any]:
    host, tenant, site = config["host"], config["tenant"], config["site"]
    endpoint = f"https://{host}/wday/cxs/{tenant}/{site}/jobs"
    result: dict[str, Any] = {"adapter": "workday_public_cxs_jobs", "endpoint": endpoint,
                              "http_status": None, "success": False, "jobs": [], "error": ""}
    if config.get("status") != "identified":
        result["error"] = "Workday detected, but tenant/site configuration is incomplete; no request made."
        return result
    payload = {"appliedFacets": {}, "limit": 20, "offset": 0, "searchText": search_text}
    try:
        response = client.post(endpoint, json=payload, headers={"Accept": "application/json"})
        result["http_status"] = response.status_code
        if not response.is_success:
            result["error"] = f"Endpoint returned HTTP {response.status_code}"
            return result
        data = response.json()
        postings = data.get("jobPostings", []) if isinstance(data, dict) else []
        jobs = []
        for item in postings[:MAX_JOBS]:
            if not isinstance(item, dict):
                continue
            job = _normalise_job(item, "workday")
            path = item.get("externalPath")
            if path and not job["url"].startswith(("http://", "https://")):
                job["url"] = urljoin(f"https://{host}", str(path))
            jobs.append(job)
        if search_text:
            requisition = search_text.lower()
            jobs = [job for job in jobs if requisition in job.get("url", "").lower()]
        result["jobs"] = jobs
        result["total_jobs_reported"] = data.get("total", len(postings)) if isinstance(data, dict) else len(postings)
        if search_text and not jobs:
            result["error"] = f"No feed record matched supplied requisition '{search_text}'."
            result["success"] = False
            result["pagination"] = {"limit": payload["limit"], "offset": 0, "search_text": search_text}
            return result
        result["success"] = True
        result["pagination"] = {"limit": payload["limit"], "offset": 0, "note": "First page only."}
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
    return result


def _bamboohr_slug(final_url: str) -> str | None:
    host = urlparse(final_url).netloc.lower().split(":", 1)[0]
    match = re.fullmatch(r"([a-z0-9-]+)\.bamboohr\.com", host)
    return match.group(1) if match else None


def _extract_bamboohr(client: httpx.Client, final_url: str) -> dict[str, Any]:
    """Read BambooHR's public careers list and, for a supplied job URL, its detail endpoint."""
    parsed = urlparse(final_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    slug = _bamboohr_slug(final_url)
    result: dict[str, Any] = {"adapter": "bamboohr_public_careers_json", "endpoint": f"{origin}/careers/list",
                              "http_status": None, "success": False, "jobs": [], "error": ""}
    if not slug:
        result["error"] = "URL host is not a recognized tenant subdomain of bamboohr.com."
        return result
    try:
        response = client.get(f"{origin}/careers/list", headers={"Accept": "application/json"})
        result["http_status"] = response.status_code
        if not response.is_success:
            result["error"] = f"Public careers list returned HTTP {response.status_code}"
            return result
        payload = response.json()
        items = payload.get("result", []) if isinstance(payload, dict) else []
        result["total_jobs_reported"] = payload.get("meta", {}).get("totalCount", len(items)) if isinstance(payload, dict) else len(items)
        requested_id = re.search(r"/careers/(\d+)(?:/|$)", parsed.path)
        jobs = []
        for item in items[:MAX_JOBS]:
            if not isinstance(item, dict):
                continue
            job_id = str(item.get("id") or "")
            job_url = f"{origin}/careers/{job_id}" if job_id else ""
            loc = item.get("location") or {}
            ats_loc = item.get("atsLocation") or {}
            location = ", ".join(str(v) for v in [loc.get("city"), loc.get("state"), ats_loc.get("province"), ats_loc.get("country")] if v)
            jobs.append({"title": str(item.get("jobOpeningName") or item.get("postingTitle") or "").strip(),
                         "location": location, "department": str(item.get("departmentLabel") or "").strip(),
                         "url": job_url, "description_available": False, "source_adapter": "bamboohr"})
        if requested_id:
            target_id = requested_id.group(1)
            result["requested_job_id"] = target_id
            detail_url = f"{origin}/careers/{target_id}/detail"
            try:
                detail_response = client.get(detail_url, headers={"Accept": "application/json"})
                result["detail_endpoint"] = detail_url
                result["detail_http_status"] = detail_response.status_code
                if detail_response.is_success:
                    detail = detail_response.json()
                    if isinstance(detail, dict):
                        result["detail_response_keys"] = sorted(detail.keys())
                        opening = detail.get("result", {}).get("jobOpening", {}) if isinstance(detail.get("result"), dict) else {}
                        if not isinstance(opening, dict):
                            opening = {}
                        detail_title = str(opening.get("jobOpeningName") or opening.get("postingTitle") or "").strip()
                        description = opening.get("description") or opening.get("jobDescription") or opening.get("descriptionHtml") or ""
                        found = next((job for job in jobs if job["url"].endswith("/" + target_id)), None)
                        if found:
                            if detail_title:
                                found["title"] = detail_title
                            location = opening.get("location") or {}
                            found["location"] = ", ".join(str(v) for v in [location.get("city"), location.get("state"), location.get("addressCountry")] if v)
                            found["department"] = str(opening.get("departmentLabel") or found.get("department") or "").strip()
                        if isinstance(description, str) and description.strip():
                            description_text = BeautifulSoup(description, "html.parser").get_text(" ", strip=True)
                            if found:
                                found["description_available"] = bool(description_text)
                                found["description_excerpt"] = description_text[:1200]
                            else:
                                jobs.insert(0, {"title": detail_title, "location": "", "department": "", "url": f"{origin}/careers/{target_id}", "description_available": bool(description_text), "description_excerpt": description_text[:1200], "source_adapter": "bamboohr_detail"})
            except (httpx.HTTPError, ValueError) as exc:
                result["detail_error"] = str(exc)
            matched = [job for job in jobs if job["url"].endswith("/" + target_id)]
            if matched:
                jobs = matched
            elif result.get("detail_http_status") and result["detail_http_status"] >= 400:
                result["error"] = f"Job ID {target_id} was not found in the public list or detail endpoint."
                result["success"] = False
                return result
        result["jobs"] = jobs
        result["success"] = bool(jobs) or result["total_jobs_reported"] == 0
        if not result["success"]:
            result["error"] = "No job records were returned by the public careers list."
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
    return result



def _is_breezy_job_url(url: str) -> bool:
    parsed = urlparse(url)
    return "breezy.hr" in parsed.netloc.lower() and bool(re.match(r"^/p/[a-z0-9]+(?:-|$)", parsed.path.lower()))


def _extract_breezyhr(client: httpx.Client, page_url: str, html: str, links: list[dict[str, str]]) -> dict[str, Any]:
    """Extract published openings from observed public Breezy HR listing/detail pages."""
    parsed = urlparse(page_url)
    origin = f"{parsed.scheme}://{parsed.netloc}"
    result: dict[str, Any] = {"adapter": "breezyhr_public_html", "success": False, "jobs": [],
                              "error": "", "candidate_links_found": 0, "detail_pages_checked": 0}
    soup = BeautifulSoup(html, "html.parser")
    if _is_breezy_job_url(page_url):
        candidates = [{"label": "", "url": page_url}]
    else:
        candidates = [link for link in links if _is_breezy_job_url(link["url"])]
    unique = []
    seen = set()
    for link in candidates:
        normalized = link["url"].split("#", 1)[0]
        if normalized not in seen:
            seen.add(normalized)
            unique.append({"label": link.get("label", ""), "url": normalized})
    result["candidate_links_found"] = len(unique)
    for link in unique[:MAX_JOBS]:
        try:
            response = client.get(link["url"])
            if not response.is_success or "html" not in response.headers.get("content-type", "").lower():
                continue
            detail = BeautifulSoup(response.text, "html.parser")
            title_node = detail.find("h1") or detail.find("title")
            title = title_node.get_text(" ", strip=True) if title_node else link["label"]
            for node in detail(["script", "style", "noscript", "svg", "nav", "footer", "header"]):
                node.decompose()
            main = detail.find("main") or detail.find("article") or detail.find(id=re.compile(r"job|position|description", re.I)) or detail.body or detail
            text = re.sub(r"\\s+", " ", main.get_text(" ", strip=True)).strip()
            if not title or len(title) > 240 or len(text) < 80:
                continue
            # Remove generic page headings from the title where the page uses a branded title.
            title = re.sub(r"\\s+at\\s+.+$", "", title, flags=re.I).strip() if title.lower().startswith("apply for ") else title
            location = ""
            for node in detail.select("[class*=location], [class*=Location]"):
                candidate = node.get_text(" ", strip=True)
                if candidate and len(candidate) < 160:
                    location = candidate
                    break
            result["jobs"].append({
                "title": title, "location": location, "department": "",
                "url": str(response.url), "description_available": len(text) >= 200,
                "description_excerpt": text[:1200], "source_adapter": "breezyhr",
            })
            result["detail_pages_checked"] += 1
        except httpx.HTTPError:
            continue
    result["success"] = bool(result["jobs"])
    if not result["success"]:
        result["error"] = "No readable public Breezy HR job detail pages were extracted from observed /p/ links."
    return result


def _page_links(soup: BeautifulSoup, page_url: str) -> list[dict[str, str]]:
    links = []
    for anchor in soup.find_all("a", href=True):
        href = str(anchor["href"]).strip()
        target = urljoin(page_url, href)
        if urlparse(target).scheme in ("http", "https"):
            links.append({"label": anchor.get_text(" ", strip=True), "url": target})
    return links


def _is_job_detail_link(link: dict[str, str], base_url: str) -> bool:
    target = urlparse(link["url"])
    base = urlparse(base_url)
    if target.netloc.lower() != base.netloc.lower() or target.path == base.path:
        return False
    label = link["label"].strip().lower()
    path = target.path.lower()
    # Explicit vacancy/job path segments are strong signals; otherwise use a
    # title-like link label on a careers page, excluding navigation/actions.
    if re.search(r"/(careers?/vacanc(y|ies)|jobs?|vacanc(y|ies)|openings?)(/|$)", path):
        return True
    excluded = {"apply", "apply now", "read more", "learn more", "careers", "view all", "login"}
    return bool(label and len(label) >= 7 and label not in excluded and not label.startswith("http")) and (
        "career" in base.path.lower() or "job" in base.path.lower() or "vacanc" in base.path.lower()
    )


def _is_direct_vacancy_url(url: str) -> bool:
    return bool(re.search(r"/careers?/vacanc(y|ies)/[^/]+/?$", urlparse(url).path.lower()))


def _extract_direct_html_vacancy(response: httpx.Response) -> dict[str, Any]:
    """Treat a supplied company-hosted vacancy detail page as one vacancy."""
    soup = BeautifulSoup(response.text, "html.parser")
    title_node = soup.find("h1") or soup.find("title")
    title = title_node.get_text(" ", strip=True) if title_node else ""
    for node in soup(["script", "style", "noscript", "svg", "nav", "footer"]):
        node.decompose()
    text = re.sub(r"\s+", " ", soup.get_text(" ", strip=True)).strip()
    title = re.sub(r"^.*?\|\s*Careers\s*\|\s*Vacancy\s*\|\s*", "", title, flags=re.I).strip()
    job = {
        "title": title, "location": "", "department": "", "url": str(response.url),
        "description_available": len(text) >= 200, "description_excerpt": text[:1200],
        "source_adapter": "same_host_html_detail",
    }
    return {"adapter": "same_host_html_vacancy_detail", "success": bool(title and len(text) >= 80),
            "jobs": [job] if title and len(text) >= 80 else [], "error": "",
            "candidate_links_found": 1, "detail_pages_checked": 1}


def _extract_generic_careers(client: httpx.Client, base_url: str, links: list[dict[str, str]], supplied_response: httpx.Response | None = None) -> dict[str, Any]:
    """Extract the supplied vacancy page directly, or inspect observed listing links."""
    if supplied_response is not None and _is_direct_vacancy_url(base_url):
        return _extract_direct_html_vacancy(supplied_response)
    result: dict[str, Any] = {"adapter": "same_host_html_vacancies", "success": False,
                              "jobs": [], "error": "", "detail_pages_checked": 0}
    candidates = []
    seen = set()
    for link in links:
        if _is_job_detail_link(link, base_url) and link["url"] not in seen:
            seen.add(link["url"])
            candidates.append(link)
    for link in candidates[:MAX_DETAIL_PAGES]:
        try:
            response = client.get(link["url"])
            if not response.is_success or "html" not in response.headers.get("content-type", "").lower():
                continue
            detail = BeautifulSoup(response.text, "html.parser")
            title_node = detail.find("h1") or detail.find("title")
            title = title_node.get_text(" ", strip=True) if title_node else link["label"]
            if not title or len(title) > 240:
                title = link["label"]
            for node in detail(["script", "style", "noscript", "svg", "nav", "footer"]):
                node.decompose()
            text = re.sub(r"\s+", " ", detail.get_text(" ", strip=True)).strip()
            # Keep the normalized record compact; full source page remains reachable by URL.
            if len(text) < 80:
                continue
            result["jobs"].append({
                "title": title,
                "location": "",
                "department": "",
                "url": str(response.url),
                "description_available": len(text) >= 200,
                "description_excerpt": text[:900],
                "source_adapter": "same_host_html",
            })
            result["detail_pages_checked"] += 1
        except httpx.HTTPError:
            continue
    result["success"] = bool(result["jobs"])
    result["candidate_links_found"] = len(candidates)
    if not result["success"]:
        result["error"] = "No readable same-host vacancy detail pages were extracted from observed links."
    return result


def investigate_careers_url(url: str, *, timeout: float = TIMEOUT) -> dict[str, Any]:
    """Inspect one supplied URL, follow observed ATS links, and try supported extractors."""
    if not url.startswith(("https://", "http://")):
        raise ValueError("URL must begin with http:// or https://")
    report: dict[str, Any] = {
        "supplied_url": url, "checked_at_utc": datetime.now(timezone.utc).isoformat(),
        "http_status": None, "final_url": "", "content_type": "", "response_bytes": 0,
        "page_title": "", "page_text_excerpt": "", "ats_detected": [], "ats_evidence": [],
        "job_extraction": {"attempted": False, "success": False, "jobs": [], "adapters": [], "note": ""},
        "errors": [],
    }
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": USER_AGENT}) as client:
            response = client.get(url)
            report.update({"http_status": response.status_code, "final_url": str(response.url),
                           "content_type": response.headers.get("content-type", ""),
                           "response_bytes": len(response.content)})
            if not response.is_success:
                report["errors"].append(f"Careers page returned HTTP {response.status_code}.")
                return report
            if "html" not in report["content_type"].lower():
                report["errors"].append("Careers URL did not return HTML.")
                return report

            html = response.text
            soup = BeautifulSoup(html, "html.parser")
            title_node = soup.find("title")
            report["page_title"] = title_node.get_text(" ", strip=True) if title_node else ""
            links = _page_links(soup, str(response.url))
            clean_soup = BeautifulSoup(html, "html.parser")
            for node in clean_soup(["script", "style", "noscript", "svg"]):
                node.decompose()
            report["page_text_excerpt"] = clean_soup.get_text(" ", strip=True)[:1200]

            # Inspect observed Workday links, including links on a corporate
            # careers page that itself is not hosted by Workday.
            ats = _detect_ats(html, str(response.url), links)
            config = _workday_config(html, str(response.url)) if "workday" in ats else None
            workday_links = [x["url"] for x in links if "myworkdayjobs.com" in urlparse(x["url"]).netloc.lower()]
            if config is None and workday_links:
                ats = _unique(ats + ["workday"])
                for workday_url in workday_links[:3]:
                    try:
                        wd = client.get(workday_url)
                        if wd.is_success and "html" in wd.headers.get("content-type", "").lower():
                            config = _workday_config(wd.text, str(wd.url))
                            report["workday_landing_url"] = str(wd.url)
                            if config:
                                break
                    except httpx.HTTPError as exc:
                        report["errors"].append(f"Could not inspect observed Workday link: {exc}")
            report["ats_detected"] = ats
            if "greenhouse" in ats:
                board = _greenhouse_board(html, str(response.url))
                report["ats_evidence"].append(
                    f"Greenhouse board token '{board}' found in supplied page HTML/URL." if board
                    else "Greenhouse references found, but no board token was extracted."
                )
            if "workday" in ats:
                report["workday_config"] = config
                report["ats_evidence"].append("Workday referenced by page HTML, configuration, or an observed careers link.")

            extraction = report["job_extraction"]
            extraction["attempted"] = True
            with httpx.Client(follow_redirects=True, timeout=timeout,
                              headers={"User-Agent": USER_AGENT, "Accept": "application/json"}) as api_client:
                if "bamboohr" in ats:
                    adapter = _extract_bamboohr(api_client, str(response.url))
                    extraction["adapters"].append(adapter)
                    if adapter["success"]:
                        extraction["jobs"].extend(adapter["jobs"])
                if "breezyhr" in ats:
                    adapter = _extract_breezyhr(client, str(response.url), html, links)
                    extraction["adapters"].append(adapter)
                    if adapter["success"]:
                        extraction["jobs"].extend(adapter["jobs"])
                if "greenhouse" in ats:
                    board = _greenhouse_board(html, str(response.url))
                    if board:
                        adapter = _extract_greenhouse(api_client, board)
                        extraction["adapters"].append(adapter)
                        if adapter["success"]:
                            extraction["jobs"].extend(adapter["jobs"])
                if "workday" in ats and config:
                    supplied_path = urlparse(str(response.url)).path
                    is_workday_detail = "/details/" in supplied_path.lower()
                    requisition_match = re.search(r"_((?:R|r)\d+(?:-\d+)?)$", supplied_path)
                    requisition = requisition_match.group(1) if requisition_match else ""
                    adapter = _extract_workday(api_client, config, search_text=requisition if is_workday_detail and requisition else "")
                    if is_workday_detail:
                        adapter["requested_detail_url"] = str(response.url)
                        adapter["requested_requisition"] = requisition
                    extraction["adapters"].append(adapter)
                    if adapter["success"]:
                        extraction["jobs"].extend(adapter["jobs"])

            # For non-ATS company sites, parse the visible listing and detail pages.
            if not extraction["jobs"]:
                generic = _extract_generic_careers(client, str(response.url), links, response)
                extraction["adapters"].append(generic)
                if generic["success"]:
                    extraction["jobs"].extend(generic["jobs"])

            extraction["success"] = bool(extraction["jobs"]) or any(
                adapter.get("success") and "total_jobs_reported" in adapter
                for adapter in extraction["adapters"]
            )
            if extraction["success"]:
                extraction["note"] = "Structured ATS data or readable same-host vacancy pages were extracted; completeness still requires validation."
            elif ats:
                extraction["note"] = "ATS detected, but no jobs were extracted. Review adapter errors and site-specific structure."
            else:
                extraction["note"] = "No supported ATS detected and no readable vacancy detail pages extracted. No blind endpoint probing or application submission was attempted."
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
    json_path, markdown_path = base.with_suffix(".json"), base.with_suffix(".md")
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    extraction = report.get("job_extraction", {})
    jobs = extraction.get("jobs", []) if isinstance(extraction, dict) else []
    lines = [
        "# Careers URL Investigation", "",
        f"- Supplied URL: {report.get('supplied_url', '')}",
        f"- Final URL: {report.get('final_url', '')}",
        f"- HTTP status: {report.get('http_status', '')}",
        f"- Page title: {report.get('page_title', '')}",
        f"- ATS detected: {', '.join(report.get('ats_detected', [])) or 'none detected'}",
        f"- Extraction success: {bool(extraction.get('success', False))}",
        f"- Jobs extracted in this response: {len(jobs)}", "",
        "## Assessment", "", str(extraction.get("note", "")), "", "## ATS evidence", "",
    ]
    lines.extend([f"- {x}" for x in report.get("ats_evidence", [])] or ["- No ATS evidence recorded."])
    lines.extend(["", "## Adapter results", ""])
    adapters = extraction.get("adapters", [])
    if adapters:
        for adapter in adapters:
            lines.append(f"- **{adapter.get('adapter', 'unknown')}**: success={adapter.get('success', False)}; HTTP={adapter.get('http_status', 'n/a')}; reported jobs={adapter.get('total_jobs_reported', 'n/a')}; candidate links={adapter.get('candidate_links_found', 'n/a')}; error={adapter.get('error', '')}")
    else:
        lines.append("- No adapter was attempted.")
    lines.extend(["", "## Extracted jobs", ""])
    for job in jobs:
        lines.append(f"- **{job.get('title') or '(untitled)'}** — {job.get('location') or 'location not provided'}")
        if job.get("url"):
            lines.append(f"  - {job['url']}")
        lines.append(f"  - Description present: {job.get('description_available', False)}")
    if not jobs:
        lines.append("- No jobs were extracted.")
    if report.get("errors"):
        lines.extend(["", "## Errors", ""] + [f"- {e}" for e in report["errors"]])
    lines.extend(["", "## Limitations", "",
                  "- One run does not guarantee completeness or long-term endpoint stability.",
                  "- Workday currently requests only the first page.",
                  "- Generic extraction checks at most 25 observed same-host detail links.",
                  "- No application forms are submitted and no account-protected content is accessed.", ""])
    markdown_path.write_text("\n".join(lines), encoding="utf-8")
    return json_path, markdown_path
