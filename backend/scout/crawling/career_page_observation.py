from dataclasses import dataclass
from datetime import datetime
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import NormalizedVacancy


@dataclass(frozen=True)
class CareerPageObservation:
    requested_url: str
    final_url: str
    canonical_url: str | None
    status_code: int
    content_type: str | None
    page_title: str | None
    platform_key: str | None
    discovered_links: tuple[str, ...]
    vacancies: tuple[NormalizedVacancy, ...]
    observed_at: datetime
    outcome: str
    detail: str | None = None


@dataclass(frozen=True)
class CareerPageCrawlResult:
    observations: tuple[CareerPageObservation, ...]
    complete: bool
    failed_urls: tuple[str, ...]
    skipped_urls: tuple[str, ...]
    detail: str | None = None

    @property
    def vacancies(self) -> tuple[NormalizedVacancy, ...]:
        return tuple(job for page in self.observations for job in page.vacancies)

    def summary(self) -> dict[str, Any]:
        return {
            "pages_observed": len(self.observations),
            "vacancies_found": len(self.vacancies),
            "complete": self.complete,
            "failed_urls": list(self.failed_urls),
            "skipped_urls": list(self.skipped_urls),
        }
