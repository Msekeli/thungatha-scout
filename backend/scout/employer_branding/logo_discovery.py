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
    site = next((part for part in parsed.path.split("/") if part
                 and not re.fullmatch(r"(?i)en-[a-z]{2}", part)
                 and part.casefold() not in ignored), None)
    if not site or not re.fullmatch(r"[A-Za-z0-9_-]+", site):
        return None
    return f"https://{host}/{site}/assets/logo"


async def _fetch_workday_logo(client, page_url):
    logo_url = _workday_logo_url(page_url)
    if not logo_url:
        return None
    image = await fetch_public_resource(client, logo_url, "image/", MAX_IMAGE_BYTES)
    return image.url, page_url, "official_ats_logo"


async def _discover_from_page(client, page_url, discovered_pages):
    page = await fetch_public_resource(
        client, page_url, "text/html", MAX_IMAGE_BYTES, allow_ats_page=True
    )
    if not _same_employer_host(page_url, page.url) and not is_ats_careers_host(page.url):
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
        if (_same_employer_host(source_url, candidate)
                and is_usable_employer_logo_page_url(candidate)):
            discovered_pages.append(candidate)
    for candidate, logo_type in extract_logo_assets(html, source_url):
        try:
            image = await fetch_public_resource(
                client, candidate, "image/", MAX_IMAGE_BYTES
            )
            return image.url, source_url, logo_type
        except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
            continue
    return None


async def discover_employer_logo(
    careers_url: str | None,
    website_url: str | None = None,
    rejected_candidates: list[str] | None = None,
) -> tuple[str, str, str] | None:
    del rejected_candidates
    page_urls = []
    for value in (careers_url, website_url):
        if value and is_usable_employer_logo_page_url(value) and value not in page_urls:
            page_urls.append(value)
    if website_url:
        parsed = httpx.URL(website_url)
        homepage = str(parsed.copy_with(path="/", query=None, fragment=None))
        if is_usable_employer_logo_page_url(homepage) and homepage not in page_urls:
            page_urls.append(homepage)
    if not page_urls:
        return None
    discovered_pages = []
    async with httpx.AsyncClient(
        timeout=12, follow_redirects=False, trust_env=False,
        headers={"User-Agent": "ThungathaScout/1.0 (+employer branding discovery)"},
    ) as client:
        inspected = set()
        while page_urls and len(inspected) < MAX_BRANDING_PAGES:
            page_url = page_urls.pop(0)
            if page_url in inspected:
                continue
            inspected.add(page_url)
            try:
                result = await _discover_from_page(client, page_url, discovered_pages)
                if result:
                    return result
            except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError,
                    OSError, ValueError):
                continue
            page_urls.extend(url for url in discovered_pages if url not in inspected)
            discovered_pages.clear()
    return None
