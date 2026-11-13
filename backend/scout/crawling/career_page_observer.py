from datetime import UTC, datetime
from urllib.parse import urljoin, urlparse

from crawlee.crawlers import HttpCrawlingContext
from parsel import Selector

from scout.crawling.career_page_fingerprint import (
    fingerprint_platform,
    parse_job_postings,
)
from scout.crawling.career_page_observation import CareerPageObservation


def observe_page(
    context: HttpCrawlingContext, body: bytes, too_large: bool
) -> CareerPageObservation:
    requested = context.request.url
    final_url = context.request.loaded_url or requested
    response = context.http_response
    status = response.status_code
    content_type = response.headers.get("content-type", "").split(";")[0]
    selector = Selector(text=body.decode("utf-8", errors="replace"))
    title = selector.css("title::text").get()
    canonical = selector.css('link[rel="canonical"]::attr(href)').get()
    canonical_url = urljoin(final_url, canonical) if canonical else None
    platform = fingerprint_platform(final_url) or fingerprint_platform(requested)
    links = _career_links(selector, final_url)
    outcome = "success" if 200 <= status < 300 else "http_failure"
    detail = None
    vacancies = []
    if too_large:
        outcome = "response_too_large"
        detail = "Response exceeded configured byte limit."
    elif status in (401, 403, 429):
        outcome = "blocked" if status != 429 else "rate_limited"
    elif status >= 500:
        outcome = "transient_failure"
    elif (
        outcome == "success"
        and not platform
        and content_type
        and content_type not in ("text/html", "application/xhtml+xml")
    ):
        outcome, detail = "unsupported_content_type", content_type
    elif outcome == "success" and not platform:
        scripts = selector.css('script[type="application/ld+json"]::text').getall()
        vacancies = parse_job_postings(scripts, final_url)
    return CareerPageObservation(
        requested, final_url, canonical_url, status, content_type, title,
        platform, links, tuple(vacancies), datetime.now(UTC), outcome, detail
    )


def _career_links(selector: Selector, base_url: str) -> tuple[str, ...]:
    base_host = urlparse(base_url).hostname
    links = []
    for anchor in selector.css("a[href]"):
        href = anchor.attrib.get("href", "")
        url = urljoin(base_url, href)
        host = urlparse(url).hostname
        label = " ".join(anchor.css("::text").getall()).lower()
        terms = ("career", "job", "vacan", "position")
        if host == base_host and any(
            term in url.lower() or term in label for term in terms
        ):
            links.append(url)
        elif fingerprint_platform(url) and any(
            term in href.lower() or term in label for term in terms
        ):
            links.append(url)
    return tuple(dict.fromkeys(links))
