import httpx
import pytest
from scout.ats_adapters.workday_adapter.workday_response_mapper import (
    map_detail_response,
)
from scout.ats_adapters.workday_adapter.workday_vacancy_mapper import (
    map_workday_vacancy,
)


def test_maps_sanitized_workday_vacancy_with_all_fields() -> None:
    listing = {"title": "Compliance Head", "externalPath": "/job/Ebene/Head_R-159"}
    detail = {
        "jobPostingInfo": {
            "jobReqId": "R-159",
            "title": "Head of Compliance",
            "jobDescription": "<p>Lead advisory</p>",
            "location": "Ebene",
            "additionalLocations": ["Johannesburg", {"location": "Cape Town"}],
            "jobFamily": "Compliance",
            "externalUrl": "https://absa.wd3.myworkdayjobs.com/absa/job/R-159",
        }
    }
    vac = map_workday_vacancy(listing, detail, "absa.wd3.myworkdayjobs.com", "absa")
    assert vac.external_job_id == "R-159"
    assert vac.title == "Head of Compliance"
    assert vac.description == "<p>Lead advisory</p>"
    assert vac.location_text == "Ebene; Johannesburg; Cape Town"
    assert vac.department == "Compliance"
    assert vac.application_url == "https://absa.wd3.myworkdayjobs.com/absa/job/R-159"


def test_fallback_identifier_and_constructed_apply_url() -> None:
    listing = {"externalPath": "/job/Cape-Town/Dev_JR100", "bulletFields": ["JR100"]}
    detail = {"jobPostingInfo": {"title": "Dev", "jobDescription": "<p>Code</p>"}}
    vac = map_workday_vacancy(listing, detail, "host.wd3.myworkdayjobs.com", "site")
    assert vac.external_job_id == "JR100"
    assert (
        vac.application_url
        == "https://host.wd3.myworkdayjobs.com/en-US/site/job/Cape-Town/Dev_JR100"
    )


def test_fallback_identifier_from_path_when_no_bullets() -> None:
    listing = {"externalPath": "/job/Cape-Town/Dev_JR999"}
    detail = {"jobPostingInfo": {"title": "Dev", "jobDescription": "<p>Code</p>"}}
    vac = map_workday_vacancy(listing, detail, "host.wd3.myworkdayjobs.com", "site")
    assert vac.external_job_id == "Dev_JR999"


def test_raises_when_title_or_path_is_missing() -> None:
    with pytest.raises(ValueError, match="externalPath"):
        map_workday_vacancy({}, {"jobPostingInfo": {"title": "Dev"}}, "host", "site")
    with pytest.raises(ValueError, match="title"):
        map_workday_vacancy(
            {"externalPath": "/job/1"},
            {"jobPostingInfo": {"jobReqId": "1"}},
            "host",
            "site",
        )


def test_map_detail_response_classifies_errors() -> None:
    resp_404 = httpx.Response(404, request=httpx.Request("GET", "https://x.com"))
    assert map_detail_response(resp_404).outcome == "not_found"

    resp_bad_json = httpx.Response(
        200, content=b"invalid json", request=httpx.Request("GET", "https://x.com")
    )
    assert map_detail_response(resp_bad_json).outcome == "malformed"

    resp_no_info = httpx.Response(
        200, json={}, request=httpx.Request("GET", "https://x.com")
    )
    assert map_detail_response(resp_no_info).outcome == "malformed"
