import pytest

from scout.ats_adapters.lever_adapter.lever_url_parser import parse_lever_board_url


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



def test_lever_discovery_returns_configuration_without_retrieving_jobs() -> None:
    import asyncio

    from scout.api.lever_routes import discover_lever_source

    result = asyncio.run(discover_lever_source("https://jobs.lever.co/mamamoney"))

    assert result["detected_adapter"] == "lever"
    assert result["adapter_config"] == {"slug": "mamamoney", "region": "global"}
    assert result["board_url"] == "https://jobs.lever.co/mamamoney"
