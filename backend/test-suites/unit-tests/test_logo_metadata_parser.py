from scout.branding.logo_metadata import extract_logo_asset, extract_logo_assets


def test_prefers_structured_logo_over_same_site_icon() -> None:
    html = """
    <link rel="icon" href="/favicon.ico">
    <script type="application/ld+json">
      {"@type":"Organization","logo":{"@type":"ImageObject","url":"/brand/logo.svg"}}
    </script>
    """
    assert extract_logo_asset(html, "https://example.com/careers") == (
        "https://example.com/brand/logo.svg", "official_logo"
    )


def test_reads_multiple_json_ld_scripts_independently() -> None:
    html = """
    <script type="application/ld+json">{"@type":"WebSite"}</script>
    <script type="application/ld+json">
      {"@graph":[{"@type":"Organization","logo":"https://cdn.example.com/logo.svg"}]}
    </script>
    """
    assert extract_logo_asset(html, "https://example.com") == (
        "https://cdn.example.com/logo.svg", "official_logo"
    )


def test_supports_external_cdn_for_explicit_logo_metadata() -> None:
    html = '<meta property="og:logo" content="https://cdn.example.net/brand.png">'
    assert extract_logo_asset(html, "https://example.com") == (
        "https://cdn.example.net/brand.png", "official_logo"
    )


def test_rejects_social_image_and_foreign_favicon() -> None:
    html = """
    <meta property="og:image" content="https://cdn.example.com/social.png">
    <link rel="icon" href="https://icons.example.net/favicon.ico">
    """
    assert extract_logo_assets(html, "https://example.com") == []


def test_rejects_insecure_and_ats_logo_urls() -> None:
    html = '<meta property="og:logo" content="http://example.com/logo.png">'
    assert extract_logo_asset(html, "https://example.com") is None
    html = '<meta property="og:logo" content="https://jobs.lever.co/favicon.ico">'
    assert extract_logo_asset(html, "https://example.com") is None
