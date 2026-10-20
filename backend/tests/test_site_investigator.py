import httpx

from app.site_investigator import (
    _extract_direct_html_vacancy,
    _detect_ats,
    _greenhouse_board,
    _extract_greenhouse,
    _is_job_detail_link,
    _workday_config,
    _bamboohr_slug,
    _extract_bamboohr,
    _extract_breezyhr,
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


def test_detect_bamboohr_from_public_careers_host():
    ats = _detect_ats("<html><title>Careers</title><p>greenhouse roles and culture</p></html>", "https://aerobotics.bamboohr.com/careers/103", [])
    assert "bamboohr" in ats
    assert "greenhouse" not in ats
    assert _bamboohr_slug("https://aerobotics.bamboohr.com/careers/103") == "aerobotics"


def test_bamboohr_adapter_returns_requested_job_only():
    def handler(request):
        if request.url.path == "/careers/list":
            return httpx.Response(200, json={"meta": {"totalCount": 2}, "result": [
                {"id": "103", "jobOpeningName": "Software Engineer", "departmentLabel": "Engineering", "location": {"city": "Cape Town"}},
                {"id": "104", "jobOpeningName": "Other Role", "departmentLabel": "Operations", "location": {"city": "Remote"}},
            ]})
        if request.url.path == "/careers/103/detail":
            return httpx.Response(200, json={"meta": {}, "result": {"jobOpening": {
                "jobOpeningName": "Software Engineer",
                "departmentLabel": "Technology",
                "location": {"city": "Cape Town", "state": "Western Cape", "addressCountry": "South Africa"},
                "description": "<p>Build and maintain software systems.</p>"
            }}})
        return httpx.Response(404)

    transport = httpx.MockTransport(handler)
    with httpx.Client(transport=transport) as client:
        result = _extract_bamboohr(client, "https://aerobotics.bamboohr.com/careers/103")
    assert result["success"] is True
    assert result["total_jobs_reported"] == 2
    assert len(result["jobs"]) == 1
    assert result["jobs"][0]["title"] == "Software Engineer"
    assert result["jobs"][0]["url"] == "https://aerobotics.bamboohr.com/careers/103"
    assert result["jobs"][0]["description_available"] is True
    assert result["jobs"][0]["department"] == "Technology"
    assert result["jobs"][0]["location"] == "Cape Town, Western Cape, South Africa"
    assert result["jobs"][0]["description_excerpt"] == "Build and maintain software systems."



def test_detect_breezyhr_from_redirected_careers_host():
    ats = _detect_ats("<html><title>Openings</title></html>", "https://travellab.breezy.hr/", [])
    assert ats == ["breezyhr"]


def test_breezyhr_adapter_extracts_only_observed_job_pages():
    listing_html = """
    <html><body>
      <h1>Openings at TravelLab Africa Group</h1>
      <a href="/p/abc123-java-developer">Java Developer</a>
      <a href="/p/def456-python-developer">Python Developer</a>
      <a href="/about">About</a>
    </body></html>
    """
    links = [
        {"label": "Java Developer", "url": "https://travellab.breezy.hr/p/abc123-java-developer"},
        {"label": "Python Developer", "url": "https://travellab.breezy.hr/p/def456-python-developer"},
        {"label": "About", "url": "https://travellab.breezy.hr/about"},
    ]

    def handler(request):
        if request.url.path == "/p/abc123-java-developer":
            return httpx.Response(200, headers={"content-type": "text/html"}, text="""
                <html><body><main><h1>Java Developer</h1>
                <p>Join our technology team to build and maintain software services and APIs.</p>
                <p>Experience with Java, testing, SQL and cloud systems is useful.</p>
                </main></body></html>
            """)
        if request.url.path == "/p/def456-python-developer":
            return httpx.Response(200, headers={"content-type": "text/html"}, text="""
                <html><body><main><h1>Python Developer</h1>
                <p>Build backend applications, integrations and automation for our travel platform.</p>
                <p>Work with Python, databases and API services in a collaborative team.</p>
                </main></body></html>
            """)
        return httpx.Response(404)

    with httpx.Client(transport=httpx.MockTransport(handler), follow_redirects=True) as client:
        result = _extract_breezyhr(client, "https://travellab.breezy.hr/", listing_html, links)
    assert result["success"] is True
    assert result["candidate_links_found"] == 2
    assert result["detail_pages_checked"] == 2
    assert {job["title"] for job in result["jobs"]} == {"Java Developer", "Python Developer"}
    assert all(job["description_available"] for job in result["jobs"])
    assert all(job["source_adapter"] == "breezyhr" for job in result["jobs"])



def test_greenhouse_board_token_from_public_job_board_url():
    assert _greenhouse_board("", "https://job-boards.greenhouse.io/ozow") == "ozow"
    assert _greenhouse_board("", "https://boards.greenhouse.io/ozow/jobs/123") == "ozow"


def test_greenhouse_adapter_extracts_structured_public_jobs():
    def handler(request):
        assert request.url == "https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true"
        return httpx.Response(200, json={"jobs": [
            {
                "id": 123,
                "title": "Software Engineer",
                "location": {"name": "Cape Town, South Africa"},
                "departments": [{"name": "Engineering"}],
                "absolute_url": "https://job-boards.greenhouse.io/ozow/jobs/123",
                "content": "<p>Build and maintain software systems.</p>",
            }
        ]})

    with httpx.Client(transport=httpx.MockTransport(handler)) as client:
        result = _extract_greenhouse(client, "ozow")

    assert result["success"] is True
    assert result["total_jobs_reported"] == 1
    assert result["jobs"][0]["title"] == "Software Engineer"
    assert result["jobs"][0]["location"] == "Cape Town, South Africa"
    assert result["jobs"][0]["department"] == "Engineering"
    assert result["jobs"][0]["description_available"] is True
    assert result["jobs"][0]["url"] == "https://job-boards.greenhouse.io/ozow/jobs/123"
