from app.greenhouse_jobs import extract_greenhouse_jobs


def test_exports_all_roles_and_preserves_company_and_location_context(tmp_path):
    source = tmp_path / "discovery.json"
    source.write_text('''{
      "boards": [
        {"board_token":"ozow","board_url":"https://job-boards.greenhouse.io/ozow",
         "board_exists":true,"valid":true,"company_name":"Ozow",
         "company_identity_status":"candidate_name_needs_review",
         "company_name_candidates":["Ozow"],"jobs":[
           {"id":"1","title":"Software Engineer","location":"Cape Town, South Africa",
            "department":"Engineering","url":"https://example.com/jobs/1",
            "source_adapter":"greenhouse","description_available":true},
           {"id":"2","title":"Finance Manager","location":"Remote - US",
            "department":"Finance","url":"https://example.com/jobs/2"}
         ]},
        {"board_token":"unresolved","jobs":[
          {"title":"Customer Support","location":"",
           "url":"https://example.com/jobs/3"}
        ]}
      ]
    }''', encoding="utf-8")

    result = extract_greenhouse_jobs(source, tmp_path / "out")
    assert result["unique_jobs_extracted"] == 3
    assert result["western_cape_location_matches"] == 1
    assert result["south_africa_location_matches"] == 1
    payload = (tmp_path / "out" / "greenhouse-jobs.json").read_text(encoding="utf-8")
    assert "Finance Manager" in payload
    assert "Customer Support" in payload
    assert (tmp_path / "out" / "greenhouse-jobs.csv").exists()


def test_deduplicates_urls_ignoring_fragment_and_trailing_slash(tmp_path):
    source = tmp_path / "discovery.json"
    source.write_text('''{"boards":[
      {"board_token":"one","jobs":[
        {"title":"Role","url":"https://example.com/jobs/1/#apply"},
        {"title":"Role duplicate","url":"https://example.com/jobs/1/"}
      ]}
    ]}''', encoding="utf-8")
    result = extract_greenhouse_jobs(source, tmp_path / "out")
    assert result["unique_jobs_extracted"] == 1
