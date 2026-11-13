import asyncio
import socket

import httpx

from scout.employer_branding.logo_discovery import discover_employer_logo

PNG = (
    b"\x89PNG\r\n\x1a\n" + b"\x00" * 8
    + (200).to_bytes(4, "big") + (80).to_bytes(4, "big") + b"\x00" * 8
)


def test_registered_workday_source_precedes_employer_homepage(monkeypatch) -> None:
    board = "https://damen.wd3.myworkdayjobs.com/Damen_Careers"
    requested = []
    original = httpx.AsyncClient

    async def handler(request):
        requested.append(str(request.url))
        if request.url.path.endswith("/assets/logo"):
            return httpx.Response(
                200, headers={"content-type": "image/png"}, content=PNG
            )
        return httpx.Response(
            200, headers={"content-type": "text/html"}, text="<html/>"
        )

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
    diagnostics = []
    result = asyncio.run(
        discover_employer_logo(
            None, "https://www.damen.com", employer_name="Damen",
            source_urls=[board], diagnostics=diagnostics,
        )
    )
    assert result == (
        "https://damen.wd3.myworkdayjobs.com/Damen_Careers/assets/logo",
        board, "official_ats_logo",
    )
    assert requested[0] == board, diagnostics



def test_workday_source_page_and_logo_endpoint_are_allowed() -> None:
    from scout.employer_branding.logo_page_helpers import (
        registered_redirect,
        workday_logo_url,
    )
    from scout.employer_branding.logo_page_url_validation import (
        is_usable_employer_logo_page_url,
    )

    board = "https://damen.wd3.myworkdayjobs.com/Damen_Careers"
    assert is_usable_employer_logo_page_url(board)
    assert registered_redirect(board, ["damen.wd3.myworkdayjobs.com"])
    assert workday_logo_url(board) == (
        "https://damen.wd3.myworkdayjobs.com/Damen_Careers/assets/logo"
    )
