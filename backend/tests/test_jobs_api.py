from fastapi.testclient import TestClient

from app import jobs_api


client = TestClient(jobs_api.app)


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_greenhouse_endpoint_returns_only_cape_town_jobs(monkeypatch):
    jobs = [
        {
            "source_type": "greenhouse", "company_name": "Ozow", "company_key": "ozow",
            "source_id": "1", "title": "Software Engineer", "location": "Cape Town, South Africa",
            "additional_locations": [], "department": "Engineering", "employment_type": None,
            "posted_at": None, "closing_at": None, "description_html": "<p>Build software</p>",
            "job_url": "https://job-boards.greenhouse.io/ozow/jobs/1",
            "application_url": "https://job-boards.greenhouse.io/ozow/jobs/1",
            "status": "active", "board_url": "https://job-boards.greenhouse.io/ozow",
        },
        {
            "source_type": "greenhouse", "company_name": "Ozow", "company_key": "ozow",
            "source_id": "2", "title": "Stellenbosch Role", "location": "Stellenbosch, South Africa",
            "additional_locations": [], "department": "Engineering", "employment_type": None,
            "posted_at": None, "closing_at": None, "description_html": None,
            "job_url": "https://job-boards.greenhouse.io/ozow/jobs/2",
            "application_url": "https://job-boards.greenhouse.io/ozow/jobs/2",
            "status": "active", "board_url": "https://job-boards.greenhouse.io/ozow",
        },
    ]
    monkeypatch.setattr(jobs_api, "_fetch_greenhouse", lambda *args, **kwargs: jobs)

    response = client.get("/api/jobs/greenhouse", params={"board": "ozow", "company_name": "Ozow"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["location_scope"] == "Cape Town, South Africa"
    assert payload["fetched_count"] == 2
    assert payload["returned_count"] == 1
    assert payload["jobs"][0]["title"] == "Software Engineer"
    assert payload["jobs"][0]["source_type"] == "greenhouse"
    assert payload["jobs"][0]["application_url"].startswith("https://")


def test_greenhouse_rejects_arbitrary_board_url():
    response = client.get("/api/jobs/greenhouse", params={"board": "https://example.com"})
    assert response.status_code == 400


def test_location_filter_does_not_include_stellenbosch_or_remote_only():
    assert jobs_api._is_cape_town({"location": "Cape Town, South Africa"})
    assert not jobs_api._is_cape_town({"location": "Stellenbosch, South Africa"})
    assert not jobs_api._is_cape_town({"location": "Remote - South Africa"})
    assert jobs_api._is_cape_town({
        "location": "Johannesburg",
        "additional_locations": ["Cape Town, South Africa"],
    })


def test_workday_normalization_keeps_listing_and_application_urls_separate():
    job = jobs_api._normalize_workday_job(
        "https://myhcm.wd3.myworkdayjobs.com/en-US/Betway_Africa",
        {
            "source_id": "JR123", "title": "Engineer", "location": "Cape Town, South Africa",
            "additional_locations": [], "external_path": "/job/Cape-Town/Engineer_JR123",
            "url": "https://apply.example.com/job/JR123",
        },
        "Betway",
    )
    assert job["job_url"] == (
        "https://myhcm.wd3.myworkdayjobs.com/en-US/Betway_Africa/job/Cape-Town/Engineer_JR123"
    )
    assert job["application_url"] == "https://apply.example.com/job/JR123"
