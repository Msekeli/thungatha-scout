from datetime import timedelta

from crawlee import ConcurrencySettings
from crawlee.crawlers import HttpCrawler, HttpCrawlingContext

from scout.crawling.career_page_observation import CareerPageCrawlResult

from scout.crawling.career_page_observer import observe_page
from scout.crawling.career_page_url_validation import (
    validate_public_career_url,
    validated_discovered_links,
)
from scout.settings import Settings, get_settings


class CareerPageCrawler:
    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()

    async def crawl(self, start_url: str) -> CareerPageCrawlResult:
        if not self._settings.crawler_enabled:
            raise RuntimeError("Career-page crawling is disabled.")
        safe_start_url = validate_public_career_url(start_url)
        observations, failed, skipped = [], [], []
        crawler = HttpCrawler(
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
        async def handle_page(context: HttpCrawlingContext) -> None:
            body, too_large = await read_bounded_body(
                context, self._settings.crawler_max_response_bytes
            )
            observation = observe_page(context, body, too_large)
            observations.append(observation)
            if observation.outcome == "success" and not observation.platform_key:
                links = validated_discovered_links(observation.discovered_links)
                if links:
                    await context.add_requests(links)

        @crawler.failed_request_handler
        async def handle_failure(
            context: HttpCrawlingContext, error: Exception
        ) -> None:
            failed.append(context.request.url)

        @crawler.on_skipped_request
        async def handle_skipped(request) -> None:
            skipped.append(request.url)

        try:
            await crawler.run([safe_start_url])
        except Exception as error:
            return CareerPageCrawlResult(
                tuple(observations),
                False,
                tuple(failed),
                tuple(skipped),
                f"Crawl interrupted ({type(error).__name__}).",
            )
        complete = bool(observations) and not failed and not skipped
        complete = complete and all(item.outcome == "success" for item in observations)
        return CareerPageCrawlResult(
            tuple(observations), complete, tuple(failed), tuple(skipped)
        )


async def read_bounded_body(
    context: HttpCrawlingContext, maximum: int
) -> tuple[bytes, bool]:
    declared = context.http_response.headers.get("content-length")
    if declared and declared.isdigit() and int(declared) > maximum:
        return b"", True
    body = bytearray()
    async for chunk in context.http_response.read_stream():
        if len(body) + len(chunk) > maximum:
            return b"", True
        body.extend(chunk)
    return bytes(body), False
