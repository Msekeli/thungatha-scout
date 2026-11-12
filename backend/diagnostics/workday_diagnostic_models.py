from dataclasses import dataclass, field


@dataclass(frozen=True)
class FieldAvailability:
    has_title: bool = False
    has_description: bool = False
    has_location: bool = False
    has_external_id: bool = False
    has_application_url: bool = False


@dataclass(frozen=True)
class SampleVacancyAudit:
    external_job_id: str
    title: str
    location_text: str | None
    description_length: int
    application_url: str


@dataclass
class TargetDiagnosticResult:
    employer_id: str
    name: str
    board_url: str
    host: str = ""
    tenant: str = ""
    site: str = ""
    listing_status: int | None = None
    reported_total: int = 0
    unique_jobs_retrieved: int = 0
    pages_fetched: int = 0
    pagination_complete: bool = False
    cap_reached: bool = False
    detail_attempts: int = 0
    detail_successes: int = 0
    detail_failures: int = 0
    vacancies_normalized: int = 0
    field_audit: FieldAvailability = field(default_factory=FieldAvailability)
    samples: list[SampleVacancyAudit] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
