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


def test_validation_rejects_api_success_with_no_usable_jobs():
    with httpx.Client(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json={"jobs": [{"id": 1, "title": "", "absolute_url": ""}]})
    )) as client:
        result = validate_greenhouse_board(client, "emptyboard")

    assert result["valid"] is False
    assert result["usable_jobs"] == 0
    assert "no usable" in result["error"].lower()


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
