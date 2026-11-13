from datetime import UTC, datetime
from urllib.parse import urljoin

from crawlee.crawlers import ParselCrawlingContext

from scout.crawling.career_page_fingerprint import (
    fingerprint_platform,
    parse_job_postings,
)
from scout.crawling.career_page_observation import CareerPageObservation
from scout.settings import Settings


def observe_page(
    context: ParselCrawlingContext, settings: Settings
) -> CareerPageObservation:
    selector = context.selector
    requested = context.request.url
    final_url = context.request.loaded_url or requested
    response = context.http_response
    status = response.status_code
    content_type = response.headers.get("content-type")
    markup = selector.get()
    too_large = len(markup.encode("utf-8")) > settings.crawler_max_response_bytes
    title = selector.css("title::text").get()
    canonical = selector.css('link[rel="canonical"]::attr(href)').get()
    canonical_url = urljoin(final_url, canonical) if canonical else None
    platform = fingerprint_platform(final_url) or fingerprint_platform(requested)
    links = tuple(dict.fromkeys(
        urljoin(final_url, link)
        for link in selector.css("a[href]::attr(href)").getall()
    ))
    outcome = "success" if 200 <= status < 300 else "http_failure"
    detail = None
    vacancies = []
    if too_large:
        outcome, detail = "response_too_large", "Response exceeded configured byte limit."
    elif status in (401, 403, 429):
        outcome = "blocked" if status != 429 else "rate_limited"
    elif status >= 500:
        outcome = "transient_failure"
    elif outcome == "success" and not platform:
        scripts = selector.css('script[type="application/ld+json"]::text').getall()
        vacancies = parse_job_postings(scripts, final_url)
    return CareerPageObservation(
        requested, final_url, canonical_url, status, content_type, title,
        platform, links, tuple(vacancies), datetime.now(UTC), outcome, detail
    )
