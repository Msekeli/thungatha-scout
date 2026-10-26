"""Translate untrusted search hits into unresolved evidence-backed leads."""
from datetime import datetime
from app.application.discovery_search import SearchHit
from app.domain.discovery import (
    DiscoveryEvidence, EmployerCandidate, IdentityStatus, OrganizationType,
    ReviewState, stable_candidate_id,
)


def candidate_from_hit(hit: SearchHit, query: str, observed_at: datetime) -> EmployerCandidate:
    excerpt = f"Title: {hit.title}"
    if hit.snippet:
        excerpt += f"\nSnippet: {hit.snippet}"
    evidence = DiscoveryEvidence(
        method="ddgs_public_web_search", query=query, observed_url=str(hit.url),
        observed_at=observed_at, excerpt=excerpt[:2000],
        note=("Search lead only. The result title and snippet do not verify "
              "employer identity, Cape Town presence, or source authority."),
    )
    return EmployerCandidate(
        candidate_id=stable_candidate_id(str(hit.url)), display_name=None,
        observed_url=str(hit.url), identity_status=IdentityStatus.UNRESOLVED,
        organization_type=OrganizationType.UNRESOLVED,
        review_state=ReviewState.DISCOVERED, evidence=[evidence],
        first_seen_at=observed_at, last_checked_at=observed_at,
    )
