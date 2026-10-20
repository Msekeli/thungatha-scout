"""Free-first web search discovery for direct-employer candidates.

Search result records are leads only. This module does not claim a company is
hiring or that a URL belongs to a direct employer; verification comes later.
"""

from __future__ import annotations

import logging
import re
from collections.abc import Iterable

from ddgs import DDGS

from app.models import CompanyCandidate

logger = logging.getLogger(__name__)

DEFAULT_REGION = "Cape Town, Western Cape, South Africa"
# Job roles are retained as future filtering hints; discovery itself is company-first.
DEFAULT_ROLES = (
    "software development",
    "technology",
    "IT",
    "data",
    "AI",
    "cloud",
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

CAREERS_HINTS = (
    "career",
    "job",
    "vacanc",
    "work-with-us",
    "work-for-us",
    "opportunit",
    "talent",
)


def _normalise_url(url: str) -> str:
    return url.strip().rstrip("/").lower()


def _classify_result(url: str, title: str, snippet: str) -> tuple[str, list[str]]:
    lowered_url = url.lower()
    text = f"{title} {snippet}".lower()

    if any(hint in lowered_url for hint in AGGREGATOR_HINTS):
        return "job_board_or_aggregator", [
            "Result URL matches a known job-board/aggregator hint."
        ]

    if any(hint in text for hint in AGENCY_HINTS):
        return "possible_recruitment_agency", [
            "Search title/snippet contains recruitment-agency language."
        ]

    is_ats = any(hint in lowered_url for hint in ATS_HOST_HINTS)
    has_careers_hint = any(hint in lowered_url for hint in CAREERS_HINTS)
    mentions_company_careers = any(
        term in text
        for term in (
            "careers",
            "career opportunities",
            "join our team",
            "work with us",
            "vacancies",
            "open positions",
        )
    )

    evidence: list[str] = []
    if is_ats:
        evidence.append("Result URL matches a known applicant-tracking-system host.")
    if has_careers_hint:
        evidence.append("Result URL contains a careers/job-related path hint.")
    if mentions_company_careers:
        evidence.append("Search title/snippet mentions careers or vacancies.")

    if is_ats or has_careers_hint or mentions_company_careers:
        return "possible_direct_employer_careers_source", evidence

    return "unknown", ["Search result requires manual source classification."]


def _build_queries(
    query: str | None,
    roles: Iterable[str],
    region: str,
) -> list[str]:
    if query and query.strip():
        return [query.strip()]

    region_lower = region.lower()
    location_terms: list[str] = []
    if "cape town" in region_lower:
        location_terms.append('"Cape Town"')
    if "western cape" in region_lower:
        location_terms.append('"Western Cape"')
    if not location_terms:
        location_terms.append(f'"{region}"')
    location_clause = " OR ".join(location_terms)

    # Discover employers and their official web presence first. Do not search
    # individual job titles here: vacancy filtering is a later pipeline stage.
    company_types = (
        '"technology companies"',
        '"software companies"',
        '"software development company"',
        '"IT services company"',
        '"SaaS company"',
        '"fintech company"',
        '"AI company"',
        '"cybersecurity company"',
        '"data analytics company"',
        '"digital product company"',
        '"e-commerce company"',
        '"technology startup"',
        '"game development studio"',
        '"cloud services company"',
    )
    queries = [
        f'{company_type} ({location_clause}) South Africa -recruitment -staffing -placement -jobs-board'
        for company_type in company_types
    ]
    queries.extend(
        [
            f'"technology companies in Cape Town" -recruitment -staffing',
            f'"software companies in Cape Town" -recruitment -staffing',
            f'"tech startups in Cape Town" South Africa -recruitment',
            f'"technology companies in the Western Cape" South Africa -recruitment',
            f'"Cape Town" technology company official website',
            f'"Western Cape" software company official website',
        ]
    )
    return queries


def discover_companies(
    query: str | None = None,
    *,
    region: str = DEFAULT_REGION,
    roles: tuple[str, ...] = DEFAULT_ROLES,
    max_results_per_query: int = 8,
    backend: str = "auto",
) -> list[CompanyCandidate]:
    """Search the public web and return deduplicated employer/careers leads.

    DDGS is an unaffiliated metasearch library, not a guaranteed search API.
    Public search backends may change, block automation, or rate-limit queries.
    This function does not use a paid API key.

    Search result titles can describe a role rather than an employer. Therefore,
    candidates remain marked as needing review and their source evidence is
    retained rather than treated as verified company records.
    """
    if max_results_per_query < 1:
        raise ValueError("max_results_per_query must be at least 1")

    queries = _build_queries(query, roles, region)
    candidates: dict[str, CompanyCandidate] = {}
    successful_queries = 0
    query_errors: list[str] = []

    search = DDGS(timeout=12)
    for search_query in queries:
        try:
            results = search.text(
                search_query,
                region="za-en",
                safesearch="moderate",
                max_results=max_results_per_query,
                backend=backend,
            )
            successful_queries += 1
        except Exception as exc:
            logger.warning("Search query failed (%s): %s", search_query, exc)
            query_errors.append(f"{search_query}: {exc}")
            continue

        for result in results or []:
            url = str(result.get("href") or result.get("url") or "").strip()
            title = str(result.get("title") or "").strip()
            snippet = str(result.get("body") or result.get("snippet") or "").strip()
            if not url or not title or not url.startswith(("http://", "https://")):
                continue

            key = _normalise_url(url)
            if key in candidates:
                candidate = candidates[key]
                snippet_evidence = f"Search snippet: {snippet}" if snippet else ""
                if snippet_evidence and snippet_evidence not in candidate.evidence:
                    candidate.evidence.append(snippet_evidence)
                continue

            employer_type, evidence = _classify_result(url, title, snippet)
            host_match = re.search(r"^https?://([^/]+)", url, re.IGNORECASE)
            host = host_match.group(1).lower() if host_match else ""
            is_ats = any(hint in host for hint in ATS_HOST_HINTS)
            is_aggregator = any(hint in host for hint in AGGREGATOR_HINTS)
            origin = f"https://{host}" if host and not (is_ats or is_aggregator) else ""
            careers_url = (
                url
                if any(hint in url.lower() for hint in CAREERS_HINTS)
                else ""
            )

            candidates[key] = CompanyCandidate(
                name=title,
                source_url=url,
                snippet=snippet,
                candidate_url=url,
                region_hint=region,
                role_hints=list(roles),
                employer_type=employer_type,
                official_website_url=origin,
                careers_url=careers_url,
                discovery_method=f"ddgs:{search_query}",
                evidence=evidence
                + ([f"Search snippet: {snippet}"] if snippet else []),
                review_status="needs_review",
            )

    if successful_queries == 0 and query_errors:
        raise RuntimeError(
            "All web searches failed. Check connectivity, rate limits, or the "
            "selected search backend. First error: " + query_errors[0]
        )

    return list(candidates.values())
