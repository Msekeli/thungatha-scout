"""Free-first web search discovery for direct-employer candidates.

Search result records are leads only. This module deliberately does not claim
that a company is hiring or that a result belongs to a direct employer; those
claims require source verification.
"""

from __future__ import annotations

import re
from collections.abc import Iterable

from ddgs import DDGS

from app.models import CompanyCandidate

DEFAULT_REGION = "Cape Town, Western Cape, South Africa"
DEFAULT_ROLES = (
    "software developer",
    "web developer",
    "software engineer",
    "frontend developer",
    "backend developer",
    "full stack developer",
    "data engineer",
    "cloud engineer",
    "AI engineer",
)

ROLE_QUERY_TEMPLATE = (
    '"{role}" ("careers" OR "jobs" OR "work with us") '
    '("Cape Town" OR "Western Cape" OR South Africa) '
    '-recruitment -staffing -placement'
)

AGENCY_HINTS = (
    "recruitment agency",
    "recruitment consultancy",
    "staffing agency",
    "talent acquisition agency",
    "recruitment company",
    "employment agency",
    "job placement",
    "recruitment services",
)

AGGREGATOR_HINTS = (
    "indeed.com",
    "glassdoor.com",
    "linkedin.com/jobs",
    "careers24.com",
    "pnet.co.za",
    "jobvine.co.za",
    "adzuna.",
    "jooble.",
    "jobrapido.",
)

ATS_HOST_HINTS = (
    "greenhouse.io",
    "lever.co",
    "myworkdayjobs.com",
    "successfactors",
    "smartrecruiters.com",
    "workable.com",
    "ashbyhq.com",
    "teamtailor.com",
    "jobs.personio.com",
)

CAREERS_HINTS = ("career", "job", "vacanc", "work-with-us", "work-for-us", "opportunit", "talent")


def _normalise_url(url: str) -> str:
    return url.strip().rstrip("/")


def _classify_result(url: str, title: str, snippet: str) -> tuple[str, list[str]]:
    lowered_url = url.lower()
    text = f"{title} {snippet}".lower()
    evidence: list[str] = []

    if any(hint in lowered_url for hint in AGGREGATOR_HINTS):
        return "job_board_or_aggregator", ["Result URL matches a known job-board/aggregator hint."]

    if any(hint in text for hint in AGENCY_HINTS):
        return "possible_recruitment_agency", ["Search title/snippet contains recruitment-agency language."]

    is_ats = any(hint in lowered_url for hint in ATS_HOST_HINTS)
    has_careers_hint = any(hint in lowered_url for hint in CAREERS_HINTS)
    mentions_company_careers = any(term in text for term in ("careers", "career opportunities", "join our team", "work with us", "vacancies", "open positions"))

    if is_ats:
        evidence.append("Result URL matches a known applicant-tracking-system host.")
    if has_careers_hint:
        evidence.append("Result URL contains a careers/job-related path hint.")
    if mentions_company_careers:
        evidence.append("Search title/snippet mentions careers or vacancies.")

    if is_ats or has_careers_hint or mentions_company_careers:
        return "possible_direct_employer_careers_source", evidence

    return "unknown", ["Search result requires manual source classification."]


def _build_queries(query: str | None, roles: Iterable[str], region: str) -> list[str]:
    if query and query.strip():
        return [query.strip()]

    queries: list[str] = []
    for role in roles:
        queries.append(
            ROLE_QUERY_TEMPLATE.format(role=role)
            .replace("Cape Town", region.split(",")[0])
            .replace("Western Cape", "Western Cape")
        )
    queries.extend(
        [
            f'"software company" "Cape Town" careers South Africa',
            f'"technology company" "Western Cape" careers jobs South Africa',
            f'"software engineering" "Cape Town" "careers" employer',
        ]
    )
    return queries


def discover_companies(
    query: str | None = None,
    *,
    region: str = DEFAULT_REGION,
    roles: tuple[str, ...] = DEFAULT_ROLES,
    max_results_per_query: int = 10,
    backend: str = "auto",
) -> list[CompanyCandidate]:
    """Search the public web for employer/careers leads using the DDGS package.

    DDGS is a third-party metasearch wrapper. Results and availability vary by
    engine and may be rate-limited. No API key is configured or required by
    this prototype, but this is not a guaranteed uptime service.
    """
    candidates: dict[str, CompanyCandidate] = {}
    queries = _build_queries(query, roles, region)

    with DDGS(timeout=12) as search:
        for search_query in queries:
            try:
                results = search.text(
                    search_query,
                    region="za-en",
                    safesearch="moderate",
                    max_results=max_results_per_query,
                    backend=backend,
                )
            except Exception as exc:  # preserve other query attempts if one engine fails
                continue

            for result in results or []:
                url = str(result.get("href") or result.get("url") or "").strip()
                title = str(result.get("title") or "").strip()
                snippet = str(result.get("body") or result.get("snippet") or "").strip()
                if not url or not title:
                    continue

                key = _normalise_url(url).lower()
                if key in candidates:
                    candidate = candidates[key]
                    if snippet and snippet not in candidate.evidence:
                        candidate.evidence.append(f"Search snippet: {snippet}")
                    continue

                employer_type, evidence = _classify_result(url, title, snippet)
                host_match = re.search(r"^https?://([^/]+)", url, re.IGNORECASE)
                website_host = host_match.group(1).lower() if host_match else ""

                candidates[key] = CompanyCandidate(
                    name=title,
                    source_url=url,
                    snippet=snippet,
                    candidate_url=url,
                    region_hint=region,
                    role_hints=list(roles),
                    employer_type=employer_type,
                    official_website_url=f"https://{website_host}" if website_host else "",
                    careers_url=url if "careers" in url.lower() or "career" in url.lower() else "",
                    discovery_method=f"ddgs:{search_query}",
                    evidence=evidence + ([f"Search snippet: {snippet}"] if snippet else []),
                    review_status="needs_review",
                )

    return list(candidates.values())
