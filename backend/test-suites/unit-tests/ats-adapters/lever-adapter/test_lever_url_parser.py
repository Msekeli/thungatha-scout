import pytest
from fastapi.testclient import TestClient

from scout.api import lever_routes
from scout.ats_adapters.lever_adapter.lever_url_parser import parse_lever_board_url
from scout.main import app


@pytest.mark.parametrize(
    ("url", "slug", "region"),
    [
        ("https://jobs.lever.co/mamamoney", "mamamoney", "global"),
        ("https://jobs.eu.lever.co/example/123", "example", "eu"),
    ],
)
def test_parse_lever_board_url(url: str, slug: str, region: str) -> None:
    config, board_url = parse_lever_board_url(url)

    assert config == {"slug": slug, "region": region}
    assert board_url.endswith("/" + slug)


@pytest.mark.parametrize(
    "url",
    [
        "http://jobs.lever.co/mamamoney",
        "https://lever.co/mamamoney",
        "https://jobs.lever.co/",
        "https://jobs.lever.co/a/b/c",
        "https://jobs.lever.co:8443/mamamoney",
        "https://user@jobs.lever.co/mamamoney",
    ],
)
def test_reject_invalid_lever_board_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_lever_board_url(url)


def test_lever_discovery_returns_inspected_postings(monkeypatch) -> None:
    async def fake_inspection(url: str, company_name: str = "") -> dict:
        return {
            "outcome": "success",
            "board_token": "mamamoney",
            "board_name": company_name or None,
            "company_name": company_name,
            "jobs": [{"id": "job-1", "title": "Engineer"}],
            "pages_fetched": 1,
            "complete": True,
            "detail": None,
            "source_url": url,
            "careers_url": url,
            "board_url": "https://jobs.lever.co/mamamoney",
            "detected_adapter": "lever",
            "adapter_config": {"slug": "mamamoney", "region": "global"},
            "total_vacancies": 1,
        }

    monkeypatch.setattr(lever_routes, "inspect_lever_board", fake_inspection)
    response = TestClient(app).get(
        "/api/v1/lever/discover",
        params={
            "url": "https://jobs.lever.co/mamamoney",
            "company_name": "Mama Money",
        },
    )

    assert response.status_code == 200
    assert response.json()["detected_adapter"] == "lever"
    assert response.json()["company_name"] == "Mama Money"
    assert response.json()["jobs"][0]["title"] == "Engineer"
