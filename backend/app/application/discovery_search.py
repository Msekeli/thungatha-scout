"""Search provider contract and DDGS backend adapter."""
from typing import Callable, Protocol
from pydantic import BaseModel, Field, HttpUrl
from app.application.discovery_config import DEFAULT_SEARCH_BACKENDS


class SearchProviderError(RuntimeError):
    """No configured search backend produced a trustworthy response."""


class SearchHit(BaseModel):
    """Untrusted search result retained as candidate evidence."""
    title: str = Field(min_length=1, max_length=500)
    url: HttpUrl
    snippet: str | None = Field(default=None, max_length=2000)


class SearchProvider(Protocol):
    def search(self, query: str, *, limit: int, region: str) -> list[dict[str, object]]:
        """Return raw result mappings or raise an exception."""


class DDGSSearchProvider:
    """DDGS adapter with configurable backend selection."""
    def __init__(self, *, backends: tuple[str, ...] = DEFAULT_SEARCH_BACKENDS,
                 timeout: float = 8.0, client_factory: Callable[..., object] | None = None) -> None:
        if not backends:
            raise ValueError("At least one DDGS backend must be configured")
        self.backends = backends
        self.timeout = timeout
        self.client_factory = client_factory

    def search(self, query: str, *, limit: int, region: str) -> list[dict[str, object]]:
        factory = self.client_factory
        if factory is None:
            from ddgs import DDGS
            factory = DDGS
        failures: list[str] = []
        received_empty = False
        for backend in self.backends:
            try:
                client = factory(timeout=self.timeout)
                results = list(client.text(query, region=region, safesearch="moderate",
                                           max_results=limit, backend=backend))
            except Exception as exc:
                failures.append(f"{backend}: {type(exc).__name__}: {str(exc)[:180]}")
                continue
            if results:
                return results
            received_empty = True
        if failures:
            details = "; ".join(failures)
            if received_empty:
                details = f"At least one backend returned empty; {details}"
            raise SearchProviderError(
                "No backend returned search results. Backend errors are not "
                f"treated as proof of an empty search. {details}"
            )
        return []
