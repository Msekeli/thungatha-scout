from dataclasses import dataclass
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import AdapterOutcome


@dataclass(frozen=True)
class WorkdayListResult:
    outcome: AdapterOutcome
    postings: list[dict[str, Any]]
    total: int
    pages_fetched: int
    complete: bool
    detail: str | None = None


@dataclass(frozen=True)
class WorkdayDetailResult:
    outcome: AdapterOutcome
    posting: dict[str, Any] | None
    detail: str | None = None
