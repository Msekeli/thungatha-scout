from urllib.parse import urlparse

from scout.employer_branding.logo_url_validation import (
    InvalidLogoAsset,
    _valid_public_https_url,
    _validate_public_host,
    is_usable_employer_logo_url,
)

ATS_CAREERS_SUFFIXES = (
    ".greenhouse.io",
    ".lever.co",
    ".teamtailor.com",
    ".myworkdayjobs.com",
    ".workable.com",
)
ATS_CAREERS_HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
    "jobs.lever.co",
    "jobs.eu.lever.co",
}


def is_ats_careers_host(value: str) -> bool:
    try:
        host = (urlparse(value).hostname or "").casefold().rstrip(".")
    except ValueError:
        return False
    return host in ATS_CAREERS_HOSTS or any(
        host.endswith(suffix) for suffix in ATS_CAREERS_SUFFIXES
    )


def is_usable_employer_logo_page_url(value: str | None) -> bool:
    return _valid_public_https_url(value) and (
        is_usable_employer_logo_url(value) or is_ats_careers_host(value or "")
    )


def validate_public_logo_page_url(value: str) -> None:
    if not is_usable_employer_logo_page_url(value):
        raise InvalidLogoAsset("URL is not an allowed public careers-page URL.")
    _validate_public_host(value)
