import httpx

from scout.employer_branding.logo_crawlee_fallback import discover_with_crawlee
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
    source_urls: list[str] | None = None,
    diagnostics: list[str] | None = None,
) -> tuple[str, str, str] | None:
    del rejected_candidates
    use_crawler_fallback = diagnostics is not None
    diagnostics = diagnostics if diagnostics is not None else []
    page_urls = []
    for value in [*(source_urls or []), careers_url, website_url]:
        if value and is_usable_employer_logo_page_url(value) and value not in page_urls:
            page_urls.append(value)
    if website_url and httpx.URL(website_url).path not in {"", "/"}:
        homepage = str(
            httpx.URL(website_url).copy_with(path="/", query=None, fragment=None)
        )
        if is_usable_employer_logo_page_url(homepage) and homepage not in page_urls:
            page_urls.append(homepage)
    if not page_urls:
        diagnostics.append("NO_USABLE_SOURCE_URL")
        return None
    initial_page_urls = list(page_urls)
    allowed_hosts = [str(httpx.URL(value).host) for value in page_urls]
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
                    client,
                    page_url,
                    discovered_pages,
                    employer_name,
                    allowed_hosts,
                    diagnostics,
                )
                if result:
                    return result
            except InvalidLogoAsset as error:
                diagnostics.append(
                    "REDIRECT_IDENTITY_MISMATCH"
                    if "redirect" in str(error).casefold()
                    else "PAGE_REJECTED"
                )
            except (UnavailableLogoAsset, httpx.HTTPError, OSError):
                diagnostics.append("PAGE_UNAVAILABLE")
            except ValueError:
                diagnostics.append("PAGE_MALFORMED")
            page_urls.extend(url for url in discovered_pages if url not in inspected)
            discovered_pages.clear()
    if len(inspected) >= MAX_BRANDING_PAGES and page_urls:
        diagnostics.append("PAGE_LIMIT_REACHED")
    if use_crawler_fallback:
        try:
            result = await discover_with_crawlee(
                initial_page_urls, employer_name, diagnostics
            )
        except (OSError, RuntimeError, ValueError) as error:
            diagnostics.append(f"CRAWLEE_FAILED:{type(error).__name__}")
        else:
            if result:
                diagnostics.append("CRAWLEE_CANDIDATE_ACCEPTED")
                return result
    return None
