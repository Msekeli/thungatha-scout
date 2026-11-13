import re
from datetime import timedelta

from crawlee import ConcurrencySettings
from crawlee.crawlers import ParselCrawler, ParselCrawlingContext

from scout.crawling.career_page_observation import (
    CareerPageCrawlResult,
    CareerPageObservation,
)
from scout.crawling.career_page_observer import observe_page
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
            observation = observe_page(context, self._settings)
            observations.append(observation)
            if not observation.platform_key:
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
