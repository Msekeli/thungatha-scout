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

    # Find employers by evidence that they advertise vacancies in the target
    # geography, not by the industry's label. Employers across every sector
    # can hire software engineers, analysts, or other roles later filtered by
    # Thungatha. Keep job boards and agencies in the evidence trail; classify
    # them for review instead of excluding them from discovery.
    region_lower = region.lower()
    location_terms: list[str] = []
    if "cape town" in region_lower:
        location_terms.append('"Cape Town"')
    if "western cape" in region_lower:
        location_terms.append('"Western Cape"')
    if not location_terms:
        location_terms.append(f'"{region}"')
    location_clause = " OR ".join(location_terms)

    queries = [
        f'({location_clause}) company careers vacancies employer -recruitment-agency',
        f'({location_clause}) "join our team" jobs company',
        f'({location_clause}) "current vacancies" company careers',
        f'({location_clause}) "open positions" employer careers',
        f'({location_clause}) "jobs at" company careers',
        f'({location_clause}) "posted" "careers" company vacancies',
        f'site:job-boards.greenhouse.io ({location_clause})',
        f'site:boards.greenhouse.io ({location_clause})',
        f'site:jobs.lever.co ({location_clause})',
        f'site:myworkdayjobs.com ({location_clause})',
        f'site:jobs.smartrecruiters.com ({location_clause})',
        f'site:apply.workable.com ({location_clause})',
        f'site:jobs.ashbyhq.com ({location_clause})',
        f'site:*.breezy.hr ({location_clause})',
        f'companies hiring in Cape Town Western Cape careers page',
        f'employers advertising vacancies in Cape Town South Africa company careers',
    ]
    return queries


def discover_companies(
    query: str | None = None,
    *,
    region: str = DEFAULT_REGION,
    roles: tuple[str, ...] = DEFAULT_ROLES,
    max_results_per_query: int = 8,
    backend: str = "auto",
) -> list[CompanyCandidate]:
    """Search the public web for employers advertising in the target region.

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
