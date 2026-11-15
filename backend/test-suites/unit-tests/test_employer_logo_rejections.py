from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_metadata import extract_logo_assets


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
