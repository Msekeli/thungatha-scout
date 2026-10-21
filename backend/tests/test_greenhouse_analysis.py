from app.greenhouse_analysis import analyze_greenhouse_report, classify_job


def test_classifies_south_african_software_job():
    result = classify_job({
        "title": "Software Engineer",
        "location": "Cape Town, South Africa",
        "department": "Engineering",
        "url": "https://job-boards.greenhouse.io/example/jobs/123",
    }, "example")
    assert result["geography"] == "south_africa"
    assert result["role_relevant"] is True
    assert result["relevance_score"] == 130


def test_remote_role_is_not_assumed_south_africa_eligible():
    result = classify_job({
        "title": "Backend Engineer",
        "location": "Remote - US",
        "url": "https://job-boards.greenhouse.io/example/jobs/124",
    }, "example")
    assert result["geography"] == "remote_unspecified"
    assert result["role_relevant"] is True
    assert result["relevance_score"] == 65
    assert "confirm eligible countries" in result["review_reason"]


def test_non_technical_job_is_not_role_relevant():
    result = classify_job({
        "title": "Account Executive",
        "location": "Cape Town, South Africa",
        "url": "https://job-boards.greenhouse.io/example/jobs/125",
    }, "example")
    assert result["role_relevant"] is False
    assert result["relevance_score"] == 100


def test_report_analysis_deduplicates_urls_and_writes_outputs(tmp_path):
    report_path = tmp_path / "input.json"
    report_path.write_text('''{
      "boards": [
        {"board_token":"one","valid":true,"jobs":[
          {"title":"Software Developer","location":"Johannesburg, South Africa","url":"https://example.com/jobs/1"},
          {"title":"Software Developer","location":"Johannesburg, South Africa","url":"https://example.com/jobs/1/"}
        ]},
        {"board_token":"two","valid":false,"jobs":[
          {"title":"Software Engineer","location":"Cape Town, South Africa","url":"https://example.com/jobs/2"}
        ]}
      ]
    }''', encoding="utf-8")
    summary = analyze_greenhouse_report(report_path, tmp_path / "out")
    assert summary["unique_jobs_reviewed"] == 1
    assert summary["south_africa_software_jobs"] == 1
    assert (tmp_path / "out" / "greenhouse-job-relevance.csv").exists()
    assert (tmp_path / "out" / "greenhouse-job-relevance.json").exists()
