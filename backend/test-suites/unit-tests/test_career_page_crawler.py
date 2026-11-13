import asyncio
from types import SimpleNamespace

from scout.crawling import career_page_crawler as module


class _Response:
    status_code = 200
    headers = {"content-type": "text/html"}

    async def read_stream(self):
        yield b"<html><title>Careers</title></html>"


class _FakeCrawler:
    scenario = "success"

    def __init__(self, **kwargs):
        self.router = SimpleNamespace(default_handler=self._register)
        self.handler = None
        self.failure_handler = None
        self.skipped_handler = None

    def _register(self, callback):
        self.handler = callback
        return callback

    def failed_request_handler(self, callback):
        self.failure_handler = callback
        return callback

    def on_skipped_request(self, callback):
        self.skipped_handler = callback
        return callback

    async def run(self, urls):
        request = SimpleNamespace(url=urls[0], loaded_url=urls[0])
        context = SimpleNamespace(request=request, http_response=_Response())
        if self.scenario == "timeout":
            raise TimeoutError()
        if self.scenario == "failed":
            await self.failure_handler(context, RuntimeError())
        elif self.scenario == "skipped":
            await self.skipped_handler(request)
        else:
            await self.handler(context)


def _crawler(monkeypatch, scenario="success"):
    _FakeCrawler.scenario = scenario
    monkeypatch.setattr(module, "HttpCrawler", _FakeCrawler)
    monkeypatch.setattr(module, "validate_public_career_url", lambda url: url)
    settings = SimpleNamespace(
        crawler_enabled=True,
        crawler_max_requests_per_run=5,
        crawler_max_depth=2,
        crawler_request_timeout_seconds=10,
        crawler_max_concurrency=1,
        crawler_respect_robots_txt=True,
        crawler_max_response_bytes=1024,
    )
    return module.CareerPageCrawler(settings)


def test_successful_page_is_complete(monkeypatch):
    result = asyncio.run(_crawler(monkeypatch).crawl("https://example.com/careers"))
    assert result.complete is True
    assert len(result.observations) == 1


def test_failed_request_makes_crawl_incomplete(monkeypatch):
    result = asyncio.run(
        _crawler(monkeypatch, "failed").crawl("https://example.com/careers")
    )
    assert result.complete is False
    assert result.failed_urls == ("https://example.com/careers",)


def test_skipped_request_makes_crawl_incomplete(monkeypatch):
    result = asyncio.run(
        _crawler(monkeypatch, "skipped").crawl("https://example.com/careers")
    )
    assert result.complete is False
    assert result.skipped_urls == ("https://example.com/careers",)


def test_timeout_returns_incomplete_result(monkeypatch):
    result = asyncio.run(
        _crawler(monkeypatch, "timeout").crawl("https://example.com/careers")
    )
    assert result.complete is False
    assert result.detail == "Crawl interrupted (TimeoutError)."
