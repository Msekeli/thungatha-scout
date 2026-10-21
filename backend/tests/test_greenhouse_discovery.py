import httpx

from app.greenhouse_discovery import (
    board_token_from_url,
    greenhouse_tokens_from_html,
    validate_greenhouse_board,
)


def test_board_token_from_supported_public_urls():
    assert board_token_from_url("https://job-boards.greenhouse.io/ozow") == "ozow"
    assert board_token_from_url("https://boards.greenhouse.io/takealotcom/jobs") == "takealotcom"
    assert board_token_from_url("https://boards.greenhouse.io/embed/job_app?for=bashdotcom") == "bashdotcom"


def test_extracts_tokens_from_embedded_api_and_board_urls():
    html = """
      <script>
        const endpoint = "https://boards-api.greenhouse.io/v1/boards/ozow/jobs";
        const embed = "https://boards.greenhouse.io/embed/job_app?for=takealotgroup";
      </script>
      <a href="https://job-boards.greenhouse.io/impact">Careers</a>
    """
    assert set(greenhouse_tokens_from_html(html)) == {"ozow", "takealotgroup", "impact"}


def test_rejects_non_greenhouse_and_reserved_urls():
    assert board_token_from_url("https://example.com/careers") is None
    assert board_token_from_url("https://job-boards.greenhouse.io/jobs") is None
    assert board_token_from_url("https://job-boards.greenhouse.io/") is None


def test_validation_accepts_usable_public_job_feed_and_deduplicates_ids():
    def handler(request):
        assert request.url == "https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true"
        return httpx.Response(200, json={"jobs": [
            {
                "id": 101,
                "title": "Software Engineer",
                "location": {"name": "Cape Town, South Africa"},
                "departments": [{"name": "Engineering"}],
                "absolute_url": "https://job-boards.greenhouse.io/ozow/jobs/101",
                "content": "<p>Build software.</p>",
            },
            {
                "id": 101,
                "title": "Duplicate Software Engineer",
                "location": {"name": "Cape Town"},
                "absolute_url": "https://job-boards.greenhouse.io/ozow/jobs/101",
            },
            {
                "id": 102,
                "title": "",
                "absolute_url": "https://job-boards.greenhouse.io/ozow/jobs/102",
            },
        ]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = validate_greenhouse_board(client, "ozow")

    assert result["valid"] is True
    assert result["total_jobs_reported"] == 3
    assert result["usable_jobs"] == 1
    assert result["jobs"][0]["id"] == "101"
    assert result["jobs"][0]["title"] == "Software Engineer"


def test_validation_keeps_board_when_api_exists_but_jobs_are_unusable():
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"jobs": [{"id": 1, "title": "", "absolute_url": ""}]})
    )) as client:
        result = validate_greenhouse_board(client, "emptyboard")

    assert result["valid"] is True
    assert result["board_exists"] is True
    assert result["jobs_available"] is False
    assert result["usable_jobs"] == 0
    assert "no usable" in result["error"].lower()


def test_validation_keeps_board_when_api_returns_zero_jobs():
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"jobs": []})
    )) as client:
        result = validate_greenhouse_board(client, "quietboard")

    assert result["valid"] is True
    assert result["board_exists"] is True
    assert result["jobs_available"] is False
    assert result["total_jobs_reported"] == 0
    assert result["error"] == ""


def test_validation_records_http_errors():
    with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(404))) as client:
        result = validate_greenhouse_board(client, "missingboard")

    assert result["valid"] is False
    assert result["http_status"] == 404
    assert "404" in result["error"]



def test_default_queries_explicitly_cover_cape_town_western_cape_and_stellenbosch():
    from app.greenhouse_discovery import DEFAULT_QUERIES

    combined = "\\n".join(DEFAULT_QUERIES).casefold()
    assert "cape town" in combined
    assert "western cape" in combined
    assert "stellenbosch" in combined
    assert any("site:job-boards.greenhouse.io" in query and "stellenbosch" in query.casefold() for query in DEFAULT_QUERIES)
    assert any("site:boards.greenhouse.io" in query and "stellenbosch" in query.casefold() for query in DEFAULT_QUERIES)



def test_regional_evidence_matches_cape_town_western_cape_and_stellenbosch_without_role_filtering():
    from app.greenhouse_discovery import _regional_job_evidence

    result = _regional_job_evidence([
        {"title": "Finance Manager", "location": "Cape Town, South Africa", "url": "https://example.com/1"},
        {"title": "Software Engineer", "location": "Stellenbosch, Western Cape", "url": "https://example.com/2"},
        {"title": "Operations Lead", "location": "Western Cape, South Africa", "url": "https://example.com/3"},
        {"title": "Developer", "location": "Remote, South Africa", "url": "https://example.com/4"},
    ])

    assert result["regional_evidence_status"] == "explicit_regional_job"
    assert result["regional_job_count"] == 3
    assert result["regional_locations"] == ["Cape Town", "Stellenbosch", "Western Cape"]
    assert {job["title"] for job in result["regional_job_examples"]} == {
        "Finance Manager", "Software Engineer", "Operations Lead"
    }


def test_regional_evidence_does_not_assume_unspecified_or_remote_locations_qualify():
    from app.greenhouse_discovery import _regional_job_evidence

    result = _regional_job_evidence([
        {"title": "Engineer", "location": "Remote, South Africa", "url": "https://example.com/1"},
        {"title": "Analyst", "location": "", "url": "https://example.com/2"},
    ])

    assert result["regional_evidence_status"] == "no_explicit_regional_job"
    assert result["regional_job_count"] == 0
    assert result["regional_locations"] == []



def test_discovery_defaults_to_brave_search_backend(monkeypatch):
    import app.greenhouse_discovery as discovery

    captured = {}

    class FakeDDGS:
        def __init__(self, timeout):
            captured["timeout"] = timeout

        def text(self, query, **kwargs):
            captured["backend"] = kwargs["backend"]
            return []

    monkeypatch.setattr(discovery, "DDGS", FakeDDGS)
    report = discovery.discover_greenhouse_boards(queries=("test query",), page_inspection_limit=0)

    assert captured["backend"] == "brave"
    assert report["successful_queries"] == 1
    assert report["empty_queries"] == ["test query"]
    assert report["search_status"] == "no_results"
    assert report["failed_queries"] == []


def test_discovery_treats_ddgs_no_results_exception_as_empty_query(monkeypatch):
    import app.greenhouse_discovery as discovery

    class DDGSException(Exception):
        pass

    class FakeDDGS:
        def __init__(self, timeout):
            pass

        def text(self, query, **kwargs):
            raise DDGSException("No results found.")

    monkeypatch.setattr(discovery, "DDGS", FakeDDGS)
    report = discovery.discover_greenhouse_boards(queries=("empty query",), page_inspection_limit=0)

    assert report["successful_queries"] == 1
    assert report["empty_queries"] == ["empty query"]
    assert report["failed_queries"] == []
    assert report["search_status"] == "no_results"


def test_discovery_reports_backend_failures_without_claiming_no_results(monkeypatch):
    import app.greenhouse_discovery as discovery

    class FakeDDGS:
        def __init__(self, timeout):
            pass

        def text(self, query, **kwargs):
            raise RuntimeError("backend unavailable")

    monkeypatch.setattr(discovery, "DDGS", FakeDDGS)
    report = discovery.discover_greenhouse_boards(queries=("failed query",), page_inspection_limit=0)

    assert report["successful_queries"] == 0
    assert report["empty_queries"] == []
    assert report["search_status"] == "failed"
    assert "RuntimeError: backend unavailable" in report["failed_queries"][0]



def test_company_name_and_board_title_parsing_is_conservative():
    from app.greenhouse_discovery import _company_name_from_title, _page_title

    assert _company_name_from_title("Acme | Careers") == "Acme"
    assert _company_name_from_title("Careers at Acme") == "Acme"
    assert _company_name_from_title("Software Engineer - Cape Town") == ""
    assert _company_name_from_title("Job Application for Junior Software Engineer (AI-Enabled) at Ozow") == ""
    assert _company_name_from_title("Greenhouse") == ""
    assert _page_title("<html><head><title>Acme Careers</title></head></html>") == "Acme Careers"


def test_company_registry_csv_keeps_unverified_and_empty_job_board_leads(tmp_path):
    from app.greenhouse_discovery import save_greenhouse_discovery_report

    report = {
        "boards": [{
            "company_name": "",
            "company_identity_status": "unresolved_board_identity",
            "company_name_candidates": [],
            "greenhouse_connection_status": "board_api_not_verified",
            "board_token": "candidateboard",
            "board_url": "https://job-boards.greenhouse.io/candidateboard",
            "board_page_title": "",
            "board_page_http_status": 404,
            "api_url": "https://boards-api.greenhouse.io/v1/boards/candidateboard/jobs?content=true",
            "board_exists": False,
            "valid": False,
            "jobs_available": False,
            "http_status": 404,
            "total_jobs_reported": 0,
            "usable_jobs": 0,
            "company_evidence": [],
            "candidate_urls": ["https://job-boards.greenhouse.io/candidateboard"],
            "search_evidence": [{"query": "site:job-boards.greenhouse.io", "title": "Candidate Careers", "snippet": ""}],
            "discovery_methods": ["search-result-url"],
            "error": "HTTP 404",
            "regional_evidence_status": "no_jobs_returned",
            "regional_job_count": 0,
            "regional_locations": [],
            "regional_job_examples": [],
        }]
    }

    _, csv_path = save_greenhouse_discovery_report(report, tmp_path)
    csv_text = csv_path.read_text(encoding="utf-8-sig")

    assert "candidateboard" in csv_text
    assert "unresolved_board_identity" in csv_text
