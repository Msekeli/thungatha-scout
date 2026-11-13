import asyncio
import socket
import httpx
from scout.employer_branding.logo_discovery import discover_employer_logo
from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_metadata import extract_logo_assets

SVG = b'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 120 40"></svg>'


def mock_http(monkeypatch, handler):
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


def test_logo_elements_rank_above_generic_images():
    html = """
    <img src="/photos/team.jpg" alt="Our team">
    <header><img class="site-logo" src="/assets/company-mark.svg"></header>
    <meta property="og:image" content="/social/share-card.jpg">
    <link rel="icon" href="/favicon.ico">
    """
    assets = extract_logo_assets(html, "https://company.example/")
    assert assets == [
        ("https://company.example/assets/company-mark.svg", "official_logo")
    ]


def test_schema_organization_logo_is_extracted():
    html = """
    <script type="application/ld+json">
    {"@type":"Organization","name":"Example","logo":{"@type":"ImageObject",
    "url":"/brand/logo.svg"}}
    </script>
    """
    assert extract_logo_assets(html, "https://company.example/") == [
        ("https://company.example/brand/logo.svg", "official_logo")
    ]


def test_about_page_is_checked_when_homepage_has_no_logo(monkeypatch):
    async def handler(request):
        if request.url.path == "/":
            return httpx.Response(
                200,
                headers={"content-type": "text/html"},
                text='<a href="/about-us">About us</a>',
            )
        if request.url.path == "/about-us":
            return httpx.Response(
                200,
                headers={"content-type": "text/html"},
                text='<img class="header-logo" src="/assets/brand.svg">',
            )
        return httpx.Response(
            200, headers={"content-type": "image/svg+xml"}, content=SVG
        )

    mock_http(monkeypatch, handler)
    result = asyncio.run(discover_employer_logo(None, "https://company.example/"))
    assert result == (
        "https://company.example/assets/brand.svg",
        "https://company.example/about-us",
        "official_logo",
    )


def test_social_images_and_favicons_are_not_logo_candidates():
    html = """
    <meta property="og:image" content="/social/share.jpg">
    <link rel="apple-touch-icon" href="/apple-touch-icon.png">
    <link rel="icon" href="/favicon.ico">
    """
    assert extract_logo_assets(html, "https://company.example/") == []


def test_rejects_logo_asset_named_for_another_brand():
    html = '<img class="company-logo" src="https://cdn.example.com/synthesia-logo.svg">'
    assert extract_logo_assets(html, "https://aleph.example/", "Aleph") == []


def test_rejects_tiny_icon_and_loading_gif():
    tiny_png = (
        b"\x89PNG\r\n\x1a\n"
        + b"\x00" * 8
        + (20).to_bytes(4, "big")
        + (20).to_bytes(4, "big")
    )
    assert not has_usable_logo_dimensions(tiny_png, "image/png")
    assert not has_usable_logo_dimensions(b"GIF89a" + b"\x00" * 20, "image/gif")
