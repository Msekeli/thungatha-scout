import httpx

from scout.branding.logo_http import (
    InvalidLogoAsset,
    MAX_IMAGE_BYTES,
    UnavailableLogoAsset,
    fetch_public_resource,
    is_usable_employer_logo_url,
)
from scout.branding.logo_metadata import extract_logo_assets


def _same_employer_host(first: str, second: str) -> bool:
    def normalize(value: str) -> str:
        return (value or "").casefold().removeprefix("www.")

    return normalize(httpx.URL(first).host) == normalize(httpx.URL(second).host)


async def _discover_from_page(
    client: httpx.AsyncClient, page_url: str, rejected: list[str] | None
) -> tuple[str, str, str] | None:
    page = await fetch_public_resource(client, page_url, "text/html", MAX_IMAGE_BYTES)
    if not _same_employer_host(page_url, page.url):
        raise InvalidLogoAsset("Careers page redirected away from its employer host.")
    source_url = page.url
    html = page.content.decode("utf-8", errors="replace")
    for candidate, logo_type in extract_logo_assets(html, source_url):
        try:
            image = await fetch_public_resource(
                client, candidate, "image/", MAX_IMAGE_BYTES
            )
            return image.url, source_url, logo_type
        except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
            if rejected is not None:
                rejected.append(candidate)
    favicon = str(httpx.URL(source_url).copy_with(path="/favicon.ico", query=None))
    try:
        image = await fetch_public_resource(client, favicon, "image/", MAX_IMAGE_BYTES)
        return image.url, source_url, "official_favicon"
    except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
        return None


async def discover_employer_logo(
    careers_url: str | None,
    website_url: str | None = None,
    rejected_candidates: list[str] | None = None,
) -> tuple[str, str, str] | None:
    candidates = []
    for value in (website_url, careers_url):
        if value and is_usable_employer_logo_url(value) and value not in candidates:
            candidates.append(value)
    if not candidates:
        return None
    async with httpx.AsyncClient(
        timeout=12,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "ThungathaScout/1.0 (+employer branding discovery)"},
    ) as client:
        for page_url in candidates:
            try:
                result = await _discover_from_page(
                    client, page_url, rejected_candidates
                )
                if result:
                    return result
            except (
                InvalidLogoAsset,
                UnavailableLogoAsset,
                httpx.HTTPError,
                OSError,
                ValueError,
            ):
                continue
    return None
