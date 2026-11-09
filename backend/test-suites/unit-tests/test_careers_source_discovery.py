import asyncio

import pytest

from scout.application import careers_source_discovery as discovery


def test_discovers_lever_through_intermediate_careers_page(monkeypatch) -> None:
    async def read_page(client, url):
        if url.endswith("careers-at-theodo"):
            return url, ["/en-uk/job-offers"]
        return url, [
            "https://jobs.lever.co/theodo/b377a1f5-1f53-4498-b7d2-a175b8fd0a9f"
        ]

    async def inspect(url, company):
        return {
            "detected_adapter": "lever",
            "board_url": "https://jobs.lever.co/theodo",
            "adapter_config": {"slug": "theodo", "region": "global"},
            "company_name": company,
        }

    monkeypatch.setattr(discovery, "read_careers_page", read_page)
    monkeypatch.setattr(discovery, "_inspect_lever", inspect)
    result = asyncio.run(
        discovery.discover_careers_source(
            "https://www.theodo.com/en-uk/careers-at-theodo", "Theodo"
        )
    )
    assert result["detected_adapter"] == "lever"
    assert result["careers_url"] == "https://www.theodo.com/en-uk/careers-at-theodo"
    assert result["board_url"] == "https://jobs.lever.co/theodo"


def test_rejects_ambiguous_multiple_ats_boards(monkeypatch) -> None:
    async def read_page(client, url):
        return url, [
            "https://jobs.lever.co/example",
            "https://job-boards.greenhouse.io/example",
        ]

    monkeypatch.setattr(discovery, "read_careers_page", read_page)
    with pytest.raises(ValueError, match="unambiguous ATS board"):
        asyncio.run(
            discovery.discover_careers_source("https://example.com/careers", "Example")
        )


def test_detects_careers_page_redirect_to_lever(monkeypatch) -> None:
    async def read_page(client, url):
        return "https://jobs.lever.co/theodo", []

    async def inspect(url, company):
        return {
            "detected_adapter": "lever",
            "board_url": "https://jobs.lever.co/theodo",
            "adapter_config": {"slug": "theodo", "region": "global"},
        }

    monkeypatch.setattr(discovery, "read_careers_page", read_page)
    monkeypatch.setattr(discovery, "_inspect_lever", inspect)
    result = asyncio.run(
        discovery.discover_careers_source("https://www.theodo.com/careers", "Theodo")
    )
    assert result["detected_adapter"] == "lever"


def test_direct_greenhouse_board_keeps_greenhouse_adapter(monkeypatch) -> None:
    async def inspect(url, company):
        return {
            "detected_adapter": "greenhouse",
            "board_url": url,
            "adapter_config": {"slug": "example"},
        }

    monkeypatch.setattr(discovery, "_inspect_greenhouse", inspect)
    result = asyncio.run(
        discovery.discover_careers_source(
            "https://job-boards.greenhouse.io/example", "Example"
        )
    )
    assert result["detected_adapter"] == "greenhouse"
