#!/usr/bin/env python3
"""Run one bounded Crawlee HTTP request on Zyte Scrapy Cloud."""

import asyncio
import importlib.metadata
import platform
import time

from crawlee.crawlers import HttpCrawler, HttpCrawlingContext

TEST_URL = "https://example.com/"
REQUEST_SUCCEEDED = False


async def main() -> None:
    global REQUEST_SUCCEEDED

    started_at = time.monotonic()
    print(f"Python: {platform.python_version()}")
    print(f"Crawlee: {importlib.metadata.version('crawlee')}")
    print(f"Target: {TEST_URL}")

    crawler = HttpCrawler(
        max_requests_per_crawl=1,
        max_request_retries=0,
        retry_on_blocked=False,
        respect_robots_txt_file=True,
        configure_logging=True,
    )

    @crawler.router.default_handler
    async def handle_request(context: HttpCrawlingContext) -> None:
        global REQUEST_SUCCEEDED

        response = context.http_response
        body = await response.read()
        print(f"HTTP status: {response.status_code}")
        print(f"Response bytes: {len(body)}")
        print(f"Final URL: {context.request.loaded_url or context.request.url}")
        if response.status_code != 200 or not body:
            raise RuntimeError("Smoke-test request did not return a valid page")
        REQUEST_SUCCEEDED = True

    await crawler.run([TEST_URL])
    elapsed = time.monotonic() - started_at
    print(f"Elapsed seconds: {elapsed:.2f}")
    if not REQUEST_SUCCEEDED:
        raise RuntimeError("Crawlee smoke test failed")
    print("RESULT: SUCCESS")


if __name__ == "__main__":
    asyncio.run(main())
