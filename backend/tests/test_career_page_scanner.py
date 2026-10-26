import json
from pathlib import Path

import pytest

from scan_careers import _clean_url, _is_job_link, read_companies


def test_reads_the_company_registry():
    companies = read_companies(Path("cape_town_tech_companies.json"))
    assert len(companies) == 79
    assert companies[0]["name"] == "Specno"
    assert companies[-1]["name"] == "Kagiso Media"


def test_rejects_invalid_registry_shape(tmp_path):
    path = tmp_path / "companies.json"
    path.write_text(json.dumps({"name": "Sanlam"}), encoding="utf-8")
    with pytest.raises(ValueError, match="array"):
        read_companies(path)


def test_rejects_company_without_url(tmp_path):
    path = tmp_path / "companies.json"
    path.write_text(json.dumps([{"name": "Sanlam"}]), encoding="utf-8")
    with pytest.raises(ValueError, match="name and url"):
        read_companies(path)


def test_normalizes_fragment_and_trailing_slash():
    assert _clean_url("https://example.com/jobs/123/#apply") == "https://example.com/jobs/123"


@pytest.mark.parametrize(
    "item",
    [
        {"text": "Software Engineer", "href": "https://careers.example.com/jobs/123", "card_text": "Cape Town"},
        {"text": "Data Analyst", "href": "https://careers.sanlamcloud.co.za/Santam/go/SALES/3644501/", "card_text": "Cape Town"},
        {"text": "Software Engineer", "href": "https://jobs.lever.co/example/abc", "card_text": "Full-time"},
    ],
)
def test_recognizes_common_job_link_shapes(item):
    assert _is_job_link(item, "https://example.com/careers")


def test_ignores_generic_careers_navigation_link():
    item = {
        "text": "Careers",
        "href": "https://example.com/careers",
        "card_text": "Careers",
    }
    assert not _is_job_link(item, "https://example.com")
