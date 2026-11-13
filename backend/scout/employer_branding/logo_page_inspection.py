import re
from urllib.parse import urljoin, urlparse

import httpx

from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_ai_verification import (
    LogoAIUnavailable,
    assess_logo_image,
)
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
from scout.settings import get_settings


MAX_BRANDING_PAGES = 5
_MULTI_LABEL_SUFFIXES = {"co.za", "co.uk", "com.au", "co.nz", "com.sg"}


def _root_domain(host: str) -> str:
    labels = host.casefold().removeprefix("www.").split(".")
    suffix = ".".join(labels[-2:])
    count = 3 if suffix in _MULTI_LABEL_SUFFIXES else 2
    return ".".join(labels[-count:])


def _same_employer_host(first: str, second: str) -> bool:
    return _root_domain(httpx.URL(first).host) == _root_domain(
        httpx.URL(second).host
    )


def _registered_redirect(page_url: str, final_url: str, allowed_hosts: list[str]):
    if is_ats_careers_host(final_url):
        return True
    final_root = _root_domain(httpx.URL(final_url).host)
    return any(_root_domain(host) == final_root for host in allowed_hosts)


def _workday_logo_url(page_url: str) -> str | None:
    parsed = urlparse(page_url)
    host = (parsed.hostname or "").casefold()
    if not host.endswith(".myworkdayjobs.com"):
        return None
    ignored = {"jobs", "search", "wday", "cxs"}
    site = next(
        (
            part for part in parsed.path.split("/") if part
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


async def _ai_accepts_image(image, employer_name, diagnostics):
    if not get_settings().ai_enabled or image.content_type == "image/svg+xml":
        return True
    try:
        assessment = await assess_logo_image(
            image.content, image.content_type, employer_name
        )
    except LogoAIUnavailable:
        diagnostics.append("AI_VERIFICATION_UNAVAILABLE")
        return False
    if not assessment.is_logo or assessment.confidence < 0.82:
        diagnostics.append("AI_REJECTED_IMAGE")
        return False
    return True


async def discover_logo_on_page(
    client, page_url, discovered_pages, employer_name="",
    allowed_hosts=None, diagnostics=None,
):
    diagnostics = diagnostics if diagnostics is not None else []
    allowed_hosts = allowed_hosts or [httpx.URL(page_url).host]
    page = await fetch_public_resource(
        client, page_url, "text/html", MAX_IMAGE_BYTES, allow_ats_page=True
    )
    if not _registered_redirect(page_url, page.url, allowed_hosts):
        raise InvalidLogoAsset("Careers page redirected away from registered domains.")
    source_url = page.url
    try:
        if result := await _fetch_workday_logo(client, source_url):
            return result
    except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
        diagnostics.append("WORKDAY_LOGO_ENDPOINT_UNAVAILABLE")
    html = page.content.decode("utf-8", errors="replace")
    parser = BrandingMetadataParser()
    parser.feed(html)
    for link in parser.branding_pages:
        candidate = urljoin(source_url, link)
        if _same_employer_host(source_url, candidate) and is_usable_employer_logo_page_url(candidate):
            discovered_pages.append(candidate)
    candidates = extract_logo_assets(html, source_url, employer_name)
    if not candidates:
        diagnostics.append("NO_BRANDING_CANDIDATES")
    for candidate, logo_type in candidates:
        try:
            image = await fetch_public_resource(
                client, candidate, "image/", MAX_IMAGE_BYTES
            )
            if not has_usable_logo_dimensions(image.content, image.content_type):
                diagnostics.append("IMAGE_DIMENSIONS_REJECTED")
                continue
            if not await _ai_accepts_image(image, employer_name, diagnostics):
                continue
            return image.url, source_url, logo_type
        except InvalidLogoAsset:
            diagnostics.append("IMAGE_INVALID")
        except (UnavailableLogoAsset, httpx.HTTPError, OSError):
            diagnostics.append("IMAGE_UNAVAILABLE")
    return None
