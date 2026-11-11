from scout.branding.logo_discovery import extract_logo_url


def test_prefers_structured_employer_logo_over_social_image() -> None:
    html = """
    <html><head>
      <meta property="og:image" content="/social-card.png">
      <script type="application/ld+json">
        {"@type":"Organization","logo":{"@type":"ImageObject","url":"/brand/logo.svg"}}
      </script>
    </head></html>
    """

    assert extract_logo_url(html, "https://example.com/careers") == (
        "https://example.com/brand/logo.svg"
    )


def test_uses_open_graph_image_when_no_structured_logo_exists() -> None:
    html = '<meta property="og:image" content="https://cdn.example.com/logo.png">'

    assert extract_logo_url(html, "https://example.com/jobs") == (
        "https://cdn.example.com/logo.png"
    )


def test_does_not_use_favicon_as_employer_logo() -> None:
    html = '<link rel="icon" href="/favicon.ico">'

    assert extract_logo_url(html, "https://example.com/jobs") is None


def test_rejects_non_https_logo_urls() -> None:
    html = '<meta property="og:image" content="http://example.com/logo.png">'

    assert extract_logo_url(html, "https://example.com/jobs") is None
