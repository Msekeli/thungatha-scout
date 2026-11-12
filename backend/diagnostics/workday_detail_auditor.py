from dataclasses import dataclass, field
from typing import Any
from diagnostics.workday_diagnostic_models import (
    FieldAvailability,
    SampleVacancyAudit,
)
from scout.ats_adapters.workday_adapter.workday_cxs_client import (
    WorkdayCxsClient,
)
from scout.ats_adapters.workday_adapter.workday_vacancy_mapper import (
    map_workday_vacancy,
)


@dataclass
class DetailAuditResult:
    attempts: int = 0
    successes: int = 0
    failures: int = 0
    normalized_count: int = 0
    field_audit: FieldAvailability = field(default_factory=FieldAvailability)
    samples: list[SampleVacancyAudit] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


async def audit_workday_details(
    client: WorkdayCxsClient,
    config: dict[str, Any],
    postings: list[dict[str, Any]],
    sample_limit: int = 3,
) -> DetailAuditResult:
    res = DetailAuditResult()
    host = f"{config['host_prefix']}.myworkdayjobs.com"
    site = config["site"]
    locale = config.get("locale", "en-US")
    for job in postings[:sample_limit]:
        path = job.get("externalPath")
        if not isinstance(path, str):
            res.errors.append("Posting missing externalPath.")
            continue
        res.attempts += 1
        detail = await client.get_detail(config, path)
        if detail.posting is None:
            res.failures += 1
            res.errors.append(detail.detail or f"Failed detail for {path}")
            continue
        res.successes += 1
        try:
            vac = map_workday_vacancy(job, detail.posting, host, site, locale)
            res.normalized_count += 1
            res.field_audit = FieldAvailability(
                has_title=bool(vac.title),
                has_description=bool(vac.description),
                has_location=bool(vac.location_text),
                has_external_id=bool(vac.external_job_id),
                has_application_url=bool(vac.application_url),
            )
            res.samples.append(
                SampleVacancyAudit(
                    external_job_id=vac.external_job_id,
                    title=vac.title,
                    location_text=vac.location_text,
                    description_length=len(vac.description or ""),
                    application_url=vac.application_url,
                )
            )
        except Exception as exc:
            res.errors.append(f"Normalization failed for {path}: {exc}")
    return res
