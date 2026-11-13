from urllib.parse import urljoin

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
from scout.employer_branding.logo_page_helpers import (
    ai_accepts_image,
    fetch_workday_logo,
    registered_redirect,
    same_employer_host,
)
from scout.employer_branding.logo_page_url_validation import (
    is_usable_employer_logo_page_url,
)

MAX_BRANDING_PAGES = 5


async def discover_logo_on_page(
    client, page_url, discovered_pages, employer_name="",
    allowed_hosts=None, diagnostics=None,
):
    diagnostics = diagnostics if diagnostics is not None else []
    allowed_hosts = allowed_hosts or [httpx.URL(page_url).host]
    page = await fetch_public_resource(
        client, page_url, "text/html", MAX_IMAGE_BYTES, allow_ats_page=True
    )
    if not registered_redirect(page.url, allowed_hosts):
        raise InvalidLogoAsset("Careers page redirected away from registered domains.")
    source_url = page.url
    try:
        if result := await fetch_workday_logo(client, source_url):
            return result
    except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
        diagnostics.append("WORKDAY_LOGO_ENDPOINT_UNAVAILABLE")
    html = page.content.decode("utf-8", errors="replace")
    parser = BrandingMetadataParser()
    parser.feed(html)
    for link in parser.branding_pages:
        candidate = urljoin(source_url, link)
        if same_employer_host(source_url, candidate) and (
            is_usable_employer_logo_page_url(candidate)
        ):
            discovered_pages.append(candidate)
    candidates = extract_logo_assets(html, source_url, employer_name)
    if not candidates:
        diagnostics.append("NO_BRANDING_CANDIDATES")
    for candidate, logo_type in candidates[:8]:
        try:
            image = await fetch_public_resource(
                client, candidate, "image/", MAX_IMAGE_BYTES
            )
            if not has_usable_logo_dimensions(image.content, image.content_type):
                diagnostics.append("IMAGE_DIMENSIONS_REJECTED")
                continue
            if not await ai_accepts_image(image, employer_name, diagnostics):
                continue
            return image.url, source_url, logo_type
        except InvalidLogoAsset:
            diagnostics.append("IMAGE_INVALID")
        except (UnavailableLogoAsset, httpx.HTTPError, OSError):
            diagnostics.append("IMAGE_UNAVAILABLE")
    return None
