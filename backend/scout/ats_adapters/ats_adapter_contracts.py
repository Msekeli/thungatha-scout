from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Literal, Protocol


AdapterOutcome = Literal[
    "success",
    "empty",
    "partial",
    "not_found",
    "blocked",
    "rate_limited",
    "transient_failure",
    "malformed",
]


@dataclass(frozen=True)
class NormalizedVacancy:
    external_job_id: str
    title: str
    description: str | None
    location_text: str | None
    department: str | None
    office: str | None
    application_url: str
    published_at: str | None
    source_updated_at: str | None
    raw_payload: Mapping[str, Any]


@dataclass(frozen=True)
class ATSAdapterResult:
    outcome: AdapterOutcome
    vacancies: list[NormalizedVacancy]
    pages_fetched: int
    complete: bool
    detail: str | None = None
    total_vacancies: int | None = None


class ATSAdapter(Protocol):
    async def retrieve(
        self, source_config: Mapping[str, Any]
    ) -> ATSAdapterResult: ...

    async def close(self) -> None: ...
