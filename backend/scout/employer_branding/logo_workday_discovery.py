import httpx

from scout.employer_branding.logo_http import InvalidLogoAsset, UnavailableLogoAsset
from scout.employer_branding.logo_page_helpers import (
    fetch_workday_logo,
    workday_logo_url,
)


async def discover_workday_logo(
    client: httpx.AsyncClient, page_urls: list[str], diagnostics: list[str]
):
    for page_url in page_urls:
        if not workday_logo_url(page_url):
            continue
        try:
            if result := await fetch_workday_logo(client, page_url):
                return result
        except (InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError, OSError):
            diagnostics.append("WORKDAY_LOGO_ENDPOINT_UNAVAILABLE")
    return None
