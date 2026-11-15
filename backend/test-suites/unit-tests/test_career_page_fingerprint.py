from scout.crawling.career_page_fingerprint import (
    fingerprint_platform,
    parse_job_postings,
)


def test_fingerprints_only_known_registered_ats_hosts() -> None:
    assert fingerprint_platform("https://boards.greenhouse.io/acme") == "greenhouse"
    assert fingerprint_platform("https://jobs.lever.co/acme") == "lever"
    assert fingerprint_platform("https://tenant.myworkdayjobs.com/site") == "workday"
    assert fingerprint_platform("https://careers.acme.example/jobs") is None


def test_job_posting_json_ld_maps_stable_source_fields() -> None:
    scripts = [
        '{"@type":"JobPosting","title":"Engineer","url":'
        '"https://example.com/jobs/123","identifier":{"value":"123"},'
        '"description":"Build systems","datePosted":"2026-11-01"}'
    ]
    jobs = parse_job_postings(scripts, "https://example.com/careers")
    assert len(jobs) == 1
    assert jobs[0].external_job_id == "123"
    assert jobs[0].title == "Engineer"
    assert jobs[0].application_url == "https://example.com/jobs/123"


def test_invalid_and_non_job_json_ld_is_ignored() -> None:
    scripts = ["not-json", '{"@type":"Organization","name":"Example"}']
    assert parse_job_postings(scripts, "https://example.com/careers") == []


def test_graph_job_postings_are_supported() -> None:
    scripts = [
        '{"@graph":[{"@type":"JobPosting","title":"Analyst",'
        '"url":"https://example.com/jobs/1"}]}'
    ]
    jobs = parse_job_postings(scripts, "https://example.com")
    assert len(jobs) == 1
    assert jobs[0].external_job_id == "https://example.com/jobs/1"
