import httpx

from app.site_investigator import (
    _extract_direct_html_vacancy,
    _detect_ats,
    _greenhouse_board,
    _is_job_detail_link,
    _workday_config,
)


def test_detect_workday_from_host_and_page_config():
    html = 'window.workday = window.workday || { tenant: "relx", siteId: "relx" };'
    ats = _detect_ats(html, "https://relx.wd3.myworkdayjobs.com/relx", [])
    assert "workday" in ats
    assert _workday_config(html, "https://relx.wd3.myworkdayjobs.com/relx") == {
        "host": "relx.wd3.myworkdayjobs.com",
        "tenant": "relx",
        "site": "relx",
        "status": "identified",
    }


def test_greenhouse_board_token_requires_page_evidence():
    html = 'fetch("https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true")'
    assert _greenhouse_board(html, "https://ozow.com/jobs") == "ozow"


def test_workday_incomplete_config_is_not_marked_identified():
    config = _workday_config("", "https://relx.wd3.myworkdayjobs.com/relx")
    assert config is not None
    assert config["status"] == "incomplete_config"


def test_detect_job_detail_link_on_corporate_careers_site():
    link = {
        "label": "Junior .NET Developer",
        "url": "https://www.beingit.co.za/Careers/Vacancy/JD001",
    }
    assert _is_job_detail_link(link, "https://www.beingit.co.za/Careers")


def test_reject_external_and_application_links_for_generic_extraction():
    assert not _is_job_detail_link(
        {"label": "Apply Now", "url": "https://apply.example.com/apply/123"},
        "https://www.beingit.co.za/Careers",
    )
    assert not _is_job_detail_link(
        {"label": "Graduate .NET Developer", "url": "https://other.example/jobs/123"},
        "https://www.beingit.co.za/Careers",
    )


def test_ordinary_site_does_not_get_an_ats_guess():
    assert _detect_ats("<html><title>Careers</title></html>", "https://example.com/careers", []) == []
    assert _greenhouse_board("<html></html>", "https://example.com/careers") is None



def test_direct_beingit_vacancy_extracts_one_primary_job():
    html = """
    <html><head><title>BeingIT | Careers | Vacancy | Junior .NET Developer</title></head>
    <body><nav><a href="/Services">Services</a></nav>
    <main><h1>Junior .NET Developer</h1>
    <p>We are looking for a Junior .NET Developer to join our software team.</p>
    <p>Applicants should understand C#, .NET, SQL and web development.</p>
    </main><footer><a href="/Home/PrivacyPolicy">Privacy Policy</a></footer></body></html>
    """
    response = httpx.Response(
        200,
        headers={"content-type": "text/html"},
        text=html,
        request=httpx.Request("GET", "https://www.beingit.co.za/Careers/Vacancy/DND24100301"),
    )
    result = _extract_direct_html_vacancy(response)
    assert result["success"] is True
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["title"] == "Junior .NET Developer"
    assert result["jobs"][0]["url"].endswith("/DND24100301")
    assert "Services" not in result["jobs"][0]["title"]
