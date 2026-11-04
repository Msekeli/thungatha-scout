from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
ALLOWED_BOARD_HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
}
MAX_PAGES = 20


class GreenhouseUrlError(ValueError):
    """Raised when a URL cannot identify a public Greenhouse job board."""


@dataclass(frozen=True)
class GreenhouseResult:
    outcome: str
    board_token: str
    board_name: str | None
    jobs: list[dict[str, Any]]
    pages_fetched: int
    complete: bool
    detail: str | None = None


def parse_board_token(value: str) -> str:
    parsed = urlparse(value.strip())
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_BOARD_HOSTS:
        raise GreenhouseUrlError("URL must use a supported Greenhouse board host.")

    parts = [part for part in parsed.path.split("/") if part]
    if parsed.hostname == "boards.greenhouse.io" and parts[:1] == ["embed"]:
        token = parse_qs(parsed.query).get("for", [None])[0]
    else:
        token = parts[0] if parts else None

    if not token or not token.replace("-", "").replace("_", "").isalnum():
        raise GreenhouseUrlError("URL does not contain a valid board token.")
    return token


class GreenhouseAdapter:
    def __init__(
        self,
        client: httpx.AsyncClient | None = None,
        max_pages: int = MAX_PAGES,
    ) -> None:
        self._client = client or httpx.AsyncClient(timeout=10.0, follow_redirects=False)
        self._owns_client = client is None
        self._max_pages = max_pages

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def retrieve(self, board_token: str) -> GreenhouseResult:
        board_url = f"{API_ROOT}/{board_token}"
        try:
            board_response = await self._client.get(board_url)
            failure = self._failure(board_response, board_token)
            if failure:
                return failure
            board = board_response.json()
            if not isinstance(board, dict) or not isinstance(board.get("name"), str):
                return self._malformed(board_token, "Board metadata is malformed.")

            jobs: list[dict[str, Any]] = []
            next_url: str | None = f"{board_url}/jobs?content=true"
            pages = 0
            while next_url and pages < self._max_pages:
                if urlparse(next_url).hostname != "boards-api.greenhouse.io":
                    return self._malformed(board_token, "Pagination link host is invalid.")
                response = await self._client.get(next_url)
                failure = self._failure(response, board_token, board["name"], jobs, pages)
                if failure:
                    return failure
                payload = response.json()
                page_jobs = payload.get("jobs") if isinstance(payload, dict) else None
                if not isinstance(page_jobs, list):
                    return self._malformed(
                        board_token, "Job response does not contain a jobs array."
                    )
                if not all(self._valid_job(job) for job in page_jobs):
                    return self._malformed(
                        board_token, "One or more job records are malformed."
                    )
                jobs.extend(page_jobs)
                pages += 1
                next_link = response.links.get("next", {}).get("url")
                next_url = next_link

            complete = next_url is None
            return GreenhouseResult(
                outcome="success" if jobs else "empty",
                board_token=board_token,
                board_name=board["name"],
                jobs=jobs,
                pages_fetched=pages,
                complete=complete,
                detail=None if complete else "Maximum page count reached.",
            )
        except (httpx.TimeoutException, httpx.TransportError):
            return GreenhouseResult(
                "transient_failure", board_token, None, [], 0, False,
                "Greenhouse request failed or timed out.",
            )
        except (ValueError, TypeError):
            return self._malformed(board_token, "Greenhouse returned invalid JSON.")

    @staticmethod
    def _valid_job(job: Any) -> bool:
        return (
            isinstance(job, dict)
            and isinstance(job.get("id"), int)
            and isinstance(job.get("title"), str)
            and bool(job["title"].strip())
            and isinstance(job.get("absolute_url"), str)
        )

    @staticmethod
    def _failure(
        response: httpx.Response,
        token: str,
        board_name: str | None = None,
        jobs: list[dict[str, Any]] | None = None,
        pages: int = 0,
    ) -> GreenhouseResult | None:
        outcome = {
            403: "blocked",
            404: "not_found",
            429: "rate_limited",
        }.get(response.status_code)
        if response.status_code >= 500:
            outcome = "transient_failure"
        if outcome is None and response.is_success:
            return None
        if outcome is None:
            outcome = "malformed"
        return GreenhouseResult(
            outcome, token, board_name, jobs or [], pages, False,
            f"Greenhouse returned HTTP {response.status_code}.",
        )

    @staticmethod
    def _malformed(token: str, detail: str) -> GreenhouseResult:
        return GreenhouseResult("malformed", token, None, [], 0, False, detail)
