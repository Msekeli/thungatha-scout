from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

import httpx

API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
ALLOWED_BOARD_HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
}


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
    total_jobs: int | None = None


def parse_board_token(value: str) -> str:
    parsed = urlparse(value.strip())
    try:
        port = parsed.port
    except ValueError as exception:
        raise GreenhouseUrlError("URL contains an invalid port.") from exception
    if (
        parsed.scheme != "https"
        or parsed.hostname not in ALLOWED_BOARD_HOSTS
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        raise GreenhouseUrlError(
            "URL must use a supported HTTPS Greenhouse job-board host."
        )

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
    ) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=15.0,
            follow_redirects=False,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None

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

            response = await self._client.get(f"{board_url}/jobs?content=true")
            failure = self._failure(response, board_token, board["name"])
            if failure:
                return failure
            payload = response.json()
            jobs = payload.get("jobs") if isinstance(payload, dict) else None
            meta = payload.get("meta") if isinstance(payload, dict) else None
            total = meta.get("total") if isinstance(meta, dict) else None
            if (
                not isinstance(jobs, list)
                or not isinstance(total, int)
                or total < 0
                or not all(self._valid_job(job) for job in jobs)
            ):
                return self._malformed(
                    board_token,
                    "Job response must contain valid jobs and meta.total.",
                )

            complete = len(jobs) == total
            outcome = "partial" if not complete else "success" if jobs else "empty"
            return GreenhouseResult(
                outcome=outcome,
                board_token=board_token,
                board_name=board["name"],
                jobs=jobs,
                pages_fetched=1,
                complete=complete,
                detail=(
                    None
                    if complete
                    else f"API reported {total} jobs but returned {len(jobs)}."
                ),
                total_jobs=total,
            )
        except (httpx.TimeoutException, httpx.TransportError):
            return GreenhouseResult(
                "transient_failure",
                board_token,
                None,
                [],
                0,
                False,
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
            and job["absolute_url"].startswith(("https://", "http://"))
        )

    @staticmethod
    def _failure(
        response: httpx.Response,
        token: str,
        board_name: str | None = None,
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
            outcome,
            token,
            board_name,
            [],
            0,
            False,
            f"Greenhouse returned HTTP {response.status_code}.",
        )

    @staticmethod
    def _malformed(token: str, detail: str) -> GreenhouseResult:
        return GreenhouseResult(
            "malformed",
            token,
            None,
            [],
            0,
            False,
            detail,
        )
