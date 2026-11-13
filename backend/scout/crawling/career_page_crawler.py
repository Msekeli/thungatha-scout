import re
from datetime import UTC, datetime, timedelta
from urllib.parse import urljoin

from crawlee import ConcurrencySettings
from crawlee.crawlers import ParselCrawler, ParselCrawlingContext

from scout.crawling.career_page_fingerprint import (
    fingerprint_platform,
    parse_job_postings,
)
from scout.crawling.career_page_observation import (
    CareerPageCrawlResult,
    CareerPageObservation,
)
from scout.settings import Settings, get_settings


_CAREER_LINK = re.compile(r"(?i).*(career|jobs?|vacanc|position).*")


class CareerPageCrawler:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def crawl(self, start_url: str) -> CareerPageCrawlResult:
        if not self._settings.crawler_enabled:
            raise RuntimeError("Career-page crawling is disabled.")
        observations: list[CareerPageObservation] = []
        failed: list[str] = []
        skipped: list[str] = []
        crawler = ParselCrawler(
            max_requests_per_crawl=self._settings.crawler_max_requests_per_run,
            max_crawl_depth=self._settings.crawler_max_depth,
            max_request_retries=1,
            navigation_timeout=timedelta(
                seconds=self._settings.crawler_request_timeout_seconds
            ),
            request_handler_timeout=timedelta(
                seconds=self._settings.crawler_request_timeout_seconds
            ),
            concurrency_settings=ConcurrencySettings(
                max_concurrency=self._settings.crawler_max_concurrency
            ),
            respect_robots_txt_file=self._settings.crawler_respect_robots_txt,
            retry_on_blocked=False,
        )

        @crawler.router.default_handler
        async def handle_page(context: ParselCrawlingContext) -> None:
            observation = self._observe(context)
            observations.append(observation)
            if observation.platform_key:
                return
            await context.enqueue_links(include=[_CAREER_LINK])

        @crawler.failed_request_handler
        async def handle_failure(
            context: ParselCrawlingContext, error: Exception
        ) -> None:
            failed.append(context.request.url)

        @crawler.on_skipped_request
        async def handle_skipped(request) -> None:
            skipped.append(request.url)

        try:
            await crawler.run([start_url])
        except Exception as error:
            return CareerPageCrawlResult(
                tuple(observations), False, tuple(failed), tuple(skipped),
                f"Crawl interrupted ({type(error).__name__}).",
            )
        return CareerPageCrawlResult(
            tuple(observations), not failed, tuple(failed), tuple(skipped)
        )

    def _observe(self, context: ParselCrawlingContext) -> CareerPageObservation:
        selector = context.selector
        requested = context.request.url
        final_url = context.request.loaded_url or requested
        response = context.http_response
        status = response.status_code
        headers = response.headers
        content_type = headers.get("content-type")
        markup = selector.get()
        content_bytes = len(markup.encode("utf-8"))
        maximum = self._settings.crawler_max_response_bytes
        title = selector.css("title::text").get()
        canonical = selector.css('link[rel="canonical"]::attr(href)').get()
        canonical_url = urljoin(final_url, canonical) if canonical else None
        platform = fingerprint_platform(final_url) or fingerprint_platform(requested)
        links = tuple(
            dict.fromkeys(
                urljoin(final_url, link)
                for link in selector.css("a[href]::attr(href)").getall()
            )
        )
        outcome = "success" if 200 <= status < 300 else "http_failure"
        detail = None
        vacancies = []
        if content_bytes > maximum:
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
