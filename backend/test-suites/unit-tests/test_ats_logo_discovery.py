import asyncio
import socket

import httpx

from scout.employer_branding.logo_discovery import discover_employer_logo


def mock_http(monkeypatch, handler) -> None:
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx,
        "AsyncClient",
        lambda *args, **kwargs: original(
            *args, transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    monkeypatch.setattr(
        socket,
        "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))],
    )


def test_discovers_employer_logo_from_greenhouse_board_metadata(monkeypatch) -> None:
    html = (
        '<meta property="og:logo" content="https://cdn.example.com/employer-logo.svg">'
    )

    async def handler(request):
        if request.url.host == "boards.greenhouse.io":
            return httpx.Response(200, headers={"content-type": "text/html"}, text=html)
        return httpx.Response(
            200,
            headers={"content-type": "image/svg+xml"},
            content=b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40"></svg>',
        )

    mock_http(monkeypatch, handler)
    result = asyncio.run(discover_employer_logo("https://boards.greenhouse.io/example"))
    assert result == (
        "https://cdn.example.com/employer-logo.svg",
        "https://boards.greenhouse.io/example",
        "official_logo",
    )


def test_does_not_use_generic_ats_favicon_as_employer_logo(monkeypatch) -> None:
    html = '<link rel="icon" href="/favicon.ico">'

    async def handler(request):
        return httpx.Response(200, headers={"content-type": "text/html"}, text=html)

    mock_http(monkeypatch, handler)
    assert (
        asyncio.run(discover_employer_logo("https://boards.greenhouse.io/example"))
        is None
    )


def test_allows_greenhouse_hosted_logo_asset_but_not_board_pages() -> None:
    from scout.employer_branding.logo_http import is_usable_employer_logo_url

    assert is_usable_employer_logo_url(
        "https://recruiting.cdn.greenhouse.io/external_greenhouse_job_boards/"
        "logos/000/001/614/original/group-logo.png?1733912049"
    )
    assert not is_usable_employer_logo_url("https://boards.greenhouse.io/example")
