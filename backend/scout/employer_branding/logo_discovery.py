import httpx

from scout.employer_branding.logo_http import (
    InvalidLogoAsset,
    UnavailableLogoAsset,
)
from scout.employer_branding.logo_page_inspection import (
    MAX_BRANDING_PAGES,
    discover_logo_on_page,
)
from scout.employer_branding.logo_page_url_validation import (
    is_usable_employer_logo_page_url,
)


async def discover_employer_logo(
    careers_url: str | None,
    website_url: str | None = None,
    rejected_candidates: list[str] | None = None,
    employer_name: str = "",
) -> tuple[str, str, str] | None:
    del rejected_candidates
    page_urls = []
    for value in (website_url, careers_url):
        if value and is_usable_employer_logo_page_url(value) and value not in page_urls:
            page_urls.append(value)
    if website_url:
        homepage = str(
            httpx.URL(website_url).copy_with(path="/", query=None, fragment=None)
        )
        if is_usable_employer_logo_page_url(homepage) and homepage not in page_urls:
            page_urls.append(homepage)
    if not page_urls:
        return None
    discovered_pages = []
    async with httpx.AsyncClient(
        timeout=12,
        follow_redirects=False,
        trust_env=False,
        headers={"User-Agent": "ThungathaScout/1.0 (+employer branding discovery)"},
    ) as client:
        inspected = set()
        while page_urls and len(inspected) < MAX_BRANDING_PAGES:
            page_url = page_urls.pop(0)
            if page_url in inspected:
                continue
            inspected.add(page_url)
            try:
                result = await discover_logo_on_page(
                    client, page_url, discovered_pages, employer_name
                )
                if result:
                    return result
            except (
                InvalidLogoAsset, UnavailableLogoAsset, httpx.HTTPError,
                OSError, ValueError,
            ):
                continue
            page_urls.extend(url for url in discovered_pages if url not in inspected)
            discovered_pages.clear()
    return None
