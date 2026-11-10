import pytest

from scout.ats_adapters.teamtailor_adapter.teamtailor_url_parser import (
    parse_teamtailor_careers_url,
)


@pytest.mark.parametrize(
    "url",
    [
        "https://root.teamtailor.com/jobs",
        "https://footasylum.teamtailor.com/jobs/",
        "https://careers.teamviewer.com/jobs",
    ],
)
def test_builds_feed_url_for_hosted_and_custom_domains(url: str) -> None:
    config, feed_url = parse_teamtailor_careers_url(url)
    assert config["careers_url"] == url.rstrip("/")
    assert feed_url == url.rstrip("/") + ".rss"


@pytest.mark.parametrize(
    "url",
    [
        "http://root.teamtailor.com/jobs",
        "https://example.com/careers",
        "https://example.com/jobs?query=1",
        "https://example.com/jobs#openings",
        "https://user@example.com/jobs",
        "https://example.com:8443/jobs",
    ],
)
def test_rejects_invalid_careers_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_teamtailor_careers_url(url)
