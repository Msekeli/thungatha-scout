"""Bounded query plan and conservative URL exclusions."""
from pydantic import HttpUrl
from urllib.parse import urlsplit

DEFAULT_QUERIES = (
    '"Cape Town" company careers page',
    '"Cape Town" companies "careers" "join our team"',
    '"Cape Town" employers official careers page',
    '"Cape Town" companies "work with us"',
    '"Cape Town" company "join us" jobs',
    '"Cape Town" company website vacancies careers',
    '"Cape Town" employers "current vacancies" official website',
    '"Cape Town" companies "life at" careers',
)
MAX_QUERIES = 20
MAX_RESULTS_PER_QUERY = 10
DEFAULT_SEARCH_BACKENDS = ("brave", "duckduckgo", "mojeek")
COMPARISON_SEARCH_BACKENDS = ("bing", "brave", "duckduckgo", "mojeek")
EXCLUDED_AGGREGATOR_DOMAINS = (
    "indeed.com", "careers24.com", "simplyhired.com",
    "jobssouthafrica.co.za", "jvrjobs.co.za", "capetownjobs.co.za",
    "jobleads.com",
)


def validate_run_bounds(queries: list[str], limit: int) -> None:
    if not queries or len(queries) > MAX_QUERIES:
        raise ValueError(f"Provide between 1 and {MAX_QUERIES} queries")
    if not 1 <= limit <= MAX_RESULTS_PER_QUERY:
        raise ValueError(f"Results per query must be between 1 and {MAX_RESULTS_PER_QUERY}")
    if any(not query.strip() or len(query) > 1000 for query in queries):
        raise ValueError("Queries must be non-empty and at most 1000 characters")
    if any("cape town" not in query.lower() for query in queries):
        raise ValueError("Every query must retain the Cape Town geographic scope")


def is_aggregator_result(url: HttpUrl) -> bool:
    """Exclude known aggregators and search-result redirects."""
    parsed = urlsplit(str(url))
    host = (parsed.hostname or "").lower().rstrip(".")
    if any(host == domain or host.endswith(f".{domain}")
           for domain in EXCLUDED_AGGREGATOR_DOMAINS):
        return True
    if host == "bing.com" and parsed.path.lower().startswith("/aclick"):
        return True
    return (host == "linkedin.com" or host.endswith(".linkedin.com")) and parsed.path.lower().startswith("/jobs")
