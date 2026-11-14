import asyncio

import httpx

from scout.employer_branding.logo_discovery import discover_employer_logo
from scout.employer_branding.logo_page_helpers import workday_logo_url

from test_workday_logo_discovery import mock_http, PNG


def test_discovers_workday_logo_when_board_page_is_unavailable(monkeypatch):
    board = "https://absa.wd3.myworkdayjobs.com/ABSAcareersite"

    async def handler(request):
        if request.url.path == "/ABSAcareersite/assets/logo":
            return httpx.Response(
                200, headers={"content-type": "image/png"}, content=PNG
            )
        return httpx.Response(404)

    mock_http(monkeypatch, handler)
    assert asyncio.run(discover_employer_logo(board)) == (
        board + "/assets/logo", board, "official_ats_logo"
    )


def test_workday_endpoint_skips_locale_prefix() -> None:
    assert workday_logo_url(
        "https://firstrand.wd3.myworkdayjobs.com/en-US/FRB"
    ) == "https://firstrand.wd3.myworkdayjobs.com/FRB/assets/logo"
