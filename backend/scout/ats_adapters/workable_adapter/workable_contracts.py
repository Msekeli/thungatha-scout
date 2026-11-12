from dataclasses import dataclass
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import AdapterOutcome


@dataclass(frozen=True)
class WorkableJobsResponse:
    outcome: AdapterOutcome
    jobs: list[dict[str, Any]]
    pages_fetched: int
    complete: bool
    detail: str | None = None
