from dataclasses import dataclass
from typing import Any
from urllib.parse import parse_qs, urlparse

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
