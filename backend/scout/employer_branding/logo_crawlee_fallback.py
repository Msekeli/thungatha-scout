from datetime import timedelta

import httpx

from scout.employer_branding.branding_metadata_parser import BrandingMetadataParser
from scout.employer_branding.logo_crawlee_candidate_validation import (
    validate_crawlee_candidates,
)
from scout.employer_branding.logo_http import (
    MAX_IMAGE_BYTES,
    InvalidLogoAsset,
)
from scout.employer_branding.logo_metadata import extract_logo_assets
from scout.employer_branding.logo_page_helpers import registered_redirect
from scout.employer_branding.logo_page_url_validation import (
    is_usable_employer_logo_page_url,
)
from scout.settings import get_settings


async def discover_with_crawlee(
    page_urls: list[str], employer_name: str, diagnostics: list[str]
) -> tuple[str, str, str] | None:
    if not page_urls:
        return None
    try:
        from crawlee import ConcurrencySettings
        from crawlee.crawlers import HttpCrawler, PlaywrightCrawler
    except ImportError:
        diagnostics.append("CRAWLEE_UNAVAILABLE")
        return None
    settings = get_settings()
    if not settings.crawler_enabled:
        diagnostics.append("CRAWLER_DISABLED")
        return None
    allowed_hosts = [str(httpx.URL(url).host) for url in page_urls]
    candidates: list[tuple[str, str, str]] = []
    crawler_type = (
        PlaywrightCrawler if settings.crawler_browser_fallback_enabled else HttpCrawler
    )
    crawler = crawler_type(
        max_requests_per_crawl=min(settings.crawler_max_requests_per_run, 20),
        max_crawl_depth=min(settings.crawler_max_depth, 2),
        max_request_retries=1,
        navigation_timeout=timedelta(seconds=settings.crawler_request_timeout_seconds),
        request_handler_timeout=timedelta(
            seconds=settings.crawler_request_timeout_seconds
        ),
        concurrency_settings=ConcurrencySettings(
            max_concurrency=min(settings.crawler_max_concurrency, 3)
        ),
        respect_robots_txt_file=settings.crawler_respect_robots_txt,
        retry_on_blocked=False,
    )

    @crawler.router.default_handler
    async def handle_page(context) -> None:
        final_url = context.request.loaded_url or context.request.url
        if not registered_redirect(final_url, allowed_hosts):
            diagnostics.append("CRAWLER_REDIRECT_IDENTITY_MISMATCH")
            return
        page = getattr(context, "page", None)
        html = await page.content() if page is not None else await _read_body(context)
        parser = BrandingMetadataParser()
        parser.feed(html)
        candidates.extend(
            (url, final_url, logo_type)
            for url, logo_type in extract_logo_assets(html, final_url, employer_name)
        )
        for link in parser.branding_pages[:5]:
            if is_usable_employer_logo_page_url(str(httpx.URL(final_url).join(link))):
                await context.add_requests([str(httpx.URL(final_url).join(link))])

    @crawler.failed_request_handler
    async def handle_failure(context, error) -> None:
        diagnostics.append(f"CRAWLER_REQUEST_FAILED:{type(error).__name__}")

    await crawler.run(page_urls)
    return await validate_crawlee_candidates(candidates, employer_name, diagnostics)


async def _read_body(context) -> str:
    body = bytearray()
    async for chunk in context.http_response.read_stream():
        if len(body) + len(chunk) > MAX_IMAGE_BYTES:
            diagnostics = "CRAWLER_RESPONSE_TOO_LARGE"
            raise InvalidLogoAsset(diagnostics)
        body.extend(chunk)
    return bytes(body).decode("utf-8", errors="replace")
