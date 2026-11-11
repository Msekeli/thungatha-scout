from scout.branding.logo_discovery import (
    extract_logo_url,
    is_usable_employer_logo_url,
)


def test_prefers_structured_employer_logo_over_site_icon() -> None:
    html = """
    <html><head>
      <link rel="icon" href="/favicon.ico">
      <script type="application/ld+json">
        {"@type":"Organization","logo":{"@type":"ImageObject","url":"/brand/logo.svg"}}
      </script>
    </head></html>
    """
    assert extract_logo_url(html, "https://example.com/careers") == (
        "https://example.com/brand/logo.svg"
    )


def test_uses_official_same_site_icon_when_no_logo_metadata_exists() -> None:
    html = '<link rel="icon" href="/brand-icon.svg">'
    assert extract_logo_url(html, "https://example.com/jobs") == (
        "https://example.com/brand-icon.svg"
    )


def test_does_not_use_social_sharing_image_as_company_logo() -> None:
    html = (
        '<meta property="og:image" content="https://cdn.example.com/social-card.png">'
    )
    assert extract_logo_url(html, "https://example.com/jobs") is None


def test_does_not_use_favicon_from_another_domain() -> None:
    html = '<link rel="icon" href="https://icons.example.net/favicon.ico">'
    assert extract_logo_url(html, "https://example.com/jobs") is None


def test_does_not_use_ats_favicon_as_employer_branding() -> None:
    html = '<link rel="icon" href="/favicon.ico">'
    assert extract_logo_url(html, "https://jobs.lever.co/example") is None


def test_rejects_non_https_logo_urls() -> None:
    html = '<meta property="og:logo" content="http://example.com/logo.png">'
    assert extract_logo_url(html, "https://example.com/jobs") is None


def test_generic_favicon_services_are_not_usable_employer_logos() -> None:
    assert not is_usable_employer_logo_url(
        "https://www.google.com/s2/favicons?domain=example.com&sz=128"
    )
    assert not is_usable_employer_logo_url(
        "https://favicons.githubusercontent.com/example.com"
    )


def test_legitimate_external_logo_hosts_are_accepted() -> None:
    assert is_usable_employer_logo_url("https://cdn.example.com/company-logo.svg")
