import re
from urllib.parse import urljoin, urlparse

import httpx

from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_http import (
    InvalidLogoAsset,
    MAX_IMAGE_BYTES,
    UnavailableLogoAsset,
    fetch_public_resource,
)
from scout.employer_branding.logo_image_validation import has_usable_logo_dimensions
from scout.employer_branding.logo_metadata import extract_logo_assets
from scout.employer_branding.logo_page_url_validation import (
    is_ats_careers_host,
    is_usable_employer_logo_page_url,
)


MAX_BRANDING_PAGES = 5


def _same_employer_host(first: str, second: str) -> bool:
    def normalize(value: str) -> str:
        return (value or "").casefold().removeprefix("www.")

    return normalize(httpx.URL(first).host) == normalize(httpx.URL(second).host)


def _workday_logo_url(page_url: str) -> str | None:
    parsed = urlparse(page_url)
    host = (parsed.hostname or "").casefold()
    if not host.endswith(".myworkdayjobs.com"):
        return None
    ignored = {"jobs", "search", "wday", "cxs"}
    site = next(
        (
            part
            for part in parsed.path.split("/")
            if part
            and not re.fullmatch(r"(?i)en-[a-z]{2}", part)
            and part.casefold() not in ignored
        ),
        None,
    )
    if not site or not re.fullmatch(r"[A-Za-z0-9_-]+", site):
        return None
    return f"https://{host}/{site}/assets/logo"


async def _fetch_workday_logo(client, page_url):
    logo_url = _workday_logo_url(page_url)
    if not logo_url:
        return None
    image = await fetch_public_resource(client, logo_url, "image/", MAX_IMAGE_BYTES)
    if not has_usable_logo_dimensions(image.content, image.content_type):
        return None
    return image.url, page_url, "official_ats_logo"


async def discover_logo_on_page(client, page_url, discovered_pages, employer_name=""):
    page = await fetch_public_resource(
        client, page_url, "text/html", MAX_IMAGE_BYTES, allow_ats_page=True
    )
    if not _same_employer_host(page_url, page.url) and not is_ats_careers_host(
        page.url
    ):
        raise InvalidLogoAsset("Careers page redirected away from its employer host.")
    source_url = page.url
    try:
        if result := await _fetch_workday_logo(client, source_url):
            return result
    except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
        pass
    html = page.content.decode("utf-8", errors="replace")
    parser = BrandingMetadataParser()
    parser.feed(html)
    for link in parser.branding_pages:
        candidate = urljoin(source_url, link)
        if _same_employer_host(
            source_url, candidate
        ) and is_usable_employer_logo_page_url(candidate):
            discovered_pages.append(candidate)
    for candidate, logo_type in extract_logo_assets(html, source_url, employer_name):
        try:
            image = await fetch_public_resource(
                client, candidate, "image/", MAX_IMAGE_BYTES
            )
            if not has_usable_logo_dimensions(image.content, image.content_type):
                continue
            return image.url, source_url, logo_type
        except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
            continue
    return None
