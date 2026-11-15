from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class TeamtailorFeed:
    channel_title: str | None
    jobs: list[dict[str, Any]]


@dataclass(frozen=True)
class TeamtailorFeedResult:
    outcome: str
    jobs: list[dict[str, Any]]
    pages_fetched: int
    complete: bool
    detail: str | None = None
    channel_title: str | None = None
