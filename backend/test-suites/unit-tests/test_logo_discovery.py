import asyncio
import socket

import httpx

from scout.employer_branding.logo_discovery import discover_employer_logo
from scout.employer_branding.logo_http import is_usable_employer_logo_url


PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 24


def mock_http(monkeypatch, handler, private_hosts=()) -> None:
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
        lambda host, *args, **kwargs: [
            (
                None,
                None,
                None,
                None,
                ("127.0.0.1" if host in private_hosts else "8.8.8.8", 443),
            )
        ],
    )


def test_discovers_and_validates_external_cdn_logo(monkeypatch) -> None:
    html = '<meta property="og:logo" content="https://cdn.example.com/logo.png">'

    async def handler(request):
        if request.url.host == "employer.example.com":
            return httpx.Response(200, headers={"content-type": "text/html"}, text=html)
        return httpx.Response(200, headers={"content-type": "image/png"}, content=PNG)

    mock_http(monkeypatch, handler)
    result = asyncio.run(discover_employer_logo(None, "https://employer.example.com"))
    assert result == (
        "https://cdn.example.com/logo.png",
        "https://employer.example.com",
        "official_logo",
    )


def test_rejects_non_image_candidate(monkeypatch) -> None:
    html = '<meta property="og:logo" content="https://cdn.example.com/logo.png">'

    async def handler(request):
        if request.url.host == "employer.example.com":
            return httpx.Response(200, headers={"content-type": "text/html"}, text=html)
        return httpx.Response(
            200, headers={"content-type": "text/html"}, text="not image"
        )

    mock_http(monkeypatch, handler)
    assert (
        asyncio.run(discover_employer_logo(None, "https://employer.example.com"))
        is None
    )


def test_blocks_workable_and_ats_logo_hosts() -> None:
    assert not is_usable_employer_logo_url("https://apply.workable.com/example")
    assert not is_usable_employer_logo_url("https://jobs.lever.co/example/logo.svg")


def test_redirect_to_private_network_is_blocked(monkeypatch) -> None:
    requested = []

    async def handler(request):
        requested.append(str(request.url))
        return httpx.Response(302, headers={"location": "https://127.0.0.1/private"})

    mock_http(monkeypatch, handler, private_hosts={"127.0.0.1"})
    result = asyncio.run(discover_employer_logo(None, "https://employer.example.com"))
    assert result is None
    assert requested == ["https://employer.example.com"]



def test_registered_workday_source_is_checked_before_employer_homepage(monkeypatch) -> None:
    board = "https://damen.wd3.myworkdayjobs.com/Damen_Careers"
    requested = []

    async def handler(request):
        requested.append(str(request.url))
        if request.url.path.endswith("/assets/logo"):
            return httpx.Response(
                200, headers={"content-type": "image/png"}, content=PNG
            )
        return httpx.Response(
            200, headers={"content-type": "text/html"}, text="<html></html>"
        )

    mock_http(monkeypatch, handler)
    result = asyncio.run(
        discover_employer_logo(
            None, "https://www.damen.com", employer_name="Damen",
            source_urls=[board],
        )
    )
    assert result == (
        "https://damen.wd3.myworkdayjobs.com/Damen_Careers/assets/logo",
        board,
        "official_ats_logo",
    )
    assert requested[0] == board
