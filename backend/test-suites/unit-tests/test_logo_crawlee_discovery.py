import asyncio

import httpx

from scout.employer_branding import logo_discovery


def test_crawlee_fallback_is_invoked_after_http_discovery(monkeypatch) -> None:
    calls = []

    async def fallback(page_urls, employer_name, diagnostics):
        calls.append((page_urls, employer_name))
        return ("https://cdn.example.com/logo.svg", page_urls[0], "crawled_logo")

    async def handler(request):
        return httpx.Response(
            200,
            headers={"content-type": "text/html"},
            text="<html><body>No branding metadata</body></html>",
        )

    monkeypatch.setattr(logo_discovery, "discover_with_crawlee", fallback)
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda *args, **kwargs: original(
            *args, transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    diagnostics = []
    result = asyncio.run(
        logo_discovery.discover_employer_logo(
            None,
            "https://employer.example.com",
            employer_name="Employer",
            diagnostics=diagnostics,
        )
    )

    assert result == (
        "https://cdn.example.com/logo.svg",
        "https://employer.example.com",
        "crawled_logo",
    )
    assert calls == [(["https://employer.example.com"], "Employer")]
    assert "CRAWLEE_CANDIDATE_ACCEPTED" in diagnostics


def test_direct_discovery_does_not_start_crawler_without_diagnostics(
    monkeypatch,
) -> None:
    async def unexpected_call(*args):
        raise AssertionError("crawler should be workflow-controlled")

    async def inspect_page(*args):
        return None

    monkeypatch.setattr(logo_discovery, "discover_with_crawlee", unexpected_call)
    monkeypatch.setattr(logo_discovery, "discover_logo_on_page", inspect_page)
    result = asyncio.run(
        logo_discovery.discover_employer_logo(None, "https://employer.example.com")
    )

    assert result is None
