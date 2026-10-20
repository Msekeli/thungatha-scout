from app.discovery import _build_queries, _classify_result
from app.models import CompanyCandidate
from app.verification import CAREER_KEYWORDS


def test_careers_keywords_include_common_variants():
    assert "careers" in CAREER_KEYWORDS
    assert "vacancies" in CAREER_KEYWORDS
    assert "jobs" in CAREER_KEYWORDS


def test_build_queries_focuses_on_companies_in_local_region():
    queries = _build_queries(
        None,
        ("software developer", "web developer"),
        "Cape Town, Western Cape, South Africa",
    )
    assert len(queries) >= 10
    assert all("Cape Town" in query or "Western Cape" in query for query in queries)
    assert any('"software companies"' in query for query in queries)
    assert any('"fintech company"' in query for query in queries)
    assert not any('"software developer"' in query for query in queries)


def test_custom_query_returns_only_one_query():
    assert _build_queries("my custom query", (), "Cape Town") == ["my custom query"]


def test_aggregator_is_not_classified_as_direct_employer():
    employer_type, _ = _classify_result(
        "https://www.indeed.com/jobs?q=developer",
        "Software Developer Jobs",
        "Multiple opportunities",
    )
    assert employer_type == "job_board_or_aggregator"


def test_recruitment_agency_hint_is_kept_separate():
    employer_type, evidence = _classify_result(
        "https://example.co.za/careers",
        "Example Recruitment",
        "A specialist recruitment agency",
    )
    assert employer_type == "possible_recruitment_agency"
    assert evidence


def test_careers_page_candidate_needs_review():
    candidate = CompanyCandidate(
        name="Example Careers",
        source_url="https://example.co.za/careers",
    )
    assert candidate.review_status == "needs_review"
