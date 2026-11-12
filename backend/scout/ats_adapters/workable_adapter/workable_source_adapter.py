from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.ats_adapters.workable_adapter.workable_job_mapper import map_workable_job
from scout.ats_adapters.workable_adapter.workable_public_jobs_client import (
    WorkablePublicJobsClient,
)


class WorkableSourceAdapter:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = WorkablePublicJobsClient(client)

    async def retrieve(self, source_config: Mapping[str, Any]) -> ATSAdapterResult:
        slug = source_config.get("slug")
        if not isinstance(slug, str):
            raise TypeError("Workable source configuration requires a string slug.")
        result = await self._client.retrieve(slug)
        vacancies = []
        seen_ids = set()
        mapping_errors = 0
        for job in result.jobs:
            try:
                vacancy = map_workable_job(job)
                if vacancy.external_job_id in seen_ids:
                    raise ValueError("Duplicate Workable vacancy identifier.")
                seen_ids.add(vacancy.external_job_id)
                vacancies.append(vacancy)
            except (KeyError, TypeError, ValueError):
                mapping_errors += 1
        outcome, complete, detail = result.outcome, result.complete, result.detail
        if mapping_errors:
            if outcome in {"success", "empty"}:
                outcome = "partial"
            complete = False
            detail = f"{mapping_errors} Workable jobs failed normalization."
        return ATSAdapterResult(
            outcome,
            vacancies,
            result.pages_fetched,
            complete,
            detail,
            total_vacancies=len(vacancies) if complete else None,
        )

    async def close(self) -> None:
        await self._client.close()
