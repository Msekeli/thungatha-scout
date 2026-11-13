import asyncio
import socket

import httpx

from scout.employer_branding.logo_discovery import discover_employer_logo


PNG = (
    b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    + (120).to_bytes(4, "big") + (40).to_bytes(4, "big")
)


def mock_http(monkeypatch, handler) -> None:
    original = httpx.AsyncClient
    monkeypatch.setattr(
        httpx, "AsyncClient",
        lambda *args, **kwargs: original(
            *args, transport=httpx.MockTransport(handler), **kwargs
        ),
    )
    monkeypatch.setattr(
        socket, "getaddrinfo",
        lambda *args, **kwargs: [(None, None, None, None, ("8.8.8.8", 443))],
    )


def test_allows_official_careers_redirect_to_registered_workday_board(monkeypatch):
    html = '<meta property="og:logo" content="https://cdn.example.com/brand.png">'
    board = "https://example.wd5.myworkdayjobs.com/en-US/jobs"
    board_requests = 0

    async def handler(request):
        nonlocal board_requests
        if request.url.host == "careers.example.com":
            return httpx.Response(302, headers={"location": board})
        if request.url.host == "example.wd5.myworkdayjobs.com":
            board_requests += 1
            if board_requests == 1:
                return httpx.Response(404)
            return httpx.Response(
                200, headers={"content-type": "text/html"}, text=html
            )
        return httpx.Response(
            200, headers={"content-type": "image/png"}, content=PNG
        )

    mock_http(monkeypatch, handler)
    result = asyncio.run(discover_employer_logo(
        "https://careers.example.com/jobs", source_urls=[board]
    ))
    assert result == (
        "https://cdn.example.com/brand.png", board, "official_logo"
    )


def test_discovers_workday_logo_from_tenant_assets_endpoint(monkeypatch) -> None:
    async def handler(request):
        if request.url.path == "/SAB":
            return httpx.Response(
                200, headers={"content-type": "text/html"}, text="<html>Careers</html>"
            )
        if request.url.path == "/SAB/assets/logo":
            return httpx.Response(
                200, headers={"content-type": "image/png"}, content=PNG
            )
        return httpx.Response(404)

    mock_http(monkeypatch, handler)
    result = asyncio.run(
        discover_employer_logo("https://abinbev.wd1.myworkdayjobs.com/SAB")
    )
    assert result == (
        "https://abinbev.wd1.myworkdayjobs.com/SAB/assets/logo",
        "https://abinbev.wd1.myworkdayjobs.com/SAB",
        "official_ats_logo",
    )
