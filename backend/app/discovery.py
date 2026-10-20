"""Discovery interface; currently no provider configured."""

from app.models import CompanyCandidate


def discover_companies(query: str | None = None, *, region: str = "Cape Town, Western Cape, South Africa", roles: tuple[str, ...] = ("software developer", "web developer", "software engineer", "data engineer", "cloud engineer", "AI engineer")) -> list[CompanyCandidate]:
    """Return no candidates until an actual search provider is configured."""
    del query, region, roles
    return []
