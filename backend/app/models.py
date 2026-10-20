"""Candidate model for discovered companies."""

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class CompanyCandidate:
    """Discovery lead; not a verified employer record."""
    name: str
    source_url: str
    snippet: str = ""
    candidate_url: str = ""
    region_hint: str = ""
    role_hints: list[str] = field(default_factory=list)
    employer_type: str = "unknown"
    official_website_url: str = ""
    careers_url: str = ""
    discovery_method: str = ""
    evidence: list[str] = field(default_factory=list)
    review_status: str = "needs_review"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)
