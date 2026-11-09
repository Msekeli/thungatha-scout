from scout.ats_adapters.ats_adapter_contracts import (
    ATSAdapterResult,
    NormalizedVacancy,
)


def test_normalized_vacancy_has_provider_independent_fields() -> None:
    vacancy = NormalizedVacancy(
        external_job_id="job-123",
        title="Software Engineer",
        description="Build software",
        location_text="Cape Town, South Africa",
        department="Engineering",
        office="Cape Town",
        application_url="https://jobs.example.com/apply/123",
        published_at="2026-11-01T10:00:00Z",
        source_updated_at=None,
        raw_payload={"sourceField": "retained"},
    )

    assert vacancy.external_job_id == "job-123"
    assert vacancy.raw_payload["sourceField"] == "retained"


def test_adapter_result_distinguishes_empty_from_failure() -> None:
    result = ATSAdapterResult(
        outcome="empty", vacancies=[], pages_fetched=1, complete=True,
        total_vacancies=0,
    )

    assert result.outcome == "empty"
    assert result.complete is True
