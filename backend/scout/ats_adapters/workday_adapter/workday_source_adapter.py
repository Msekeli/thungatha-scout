import asyncio
from collections.abc import Mapping
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.ats_adapters.workday_adapter.workday_cxs_client import WorkdayCxsClient
from scout.ats_adapters.workday_adapter.workday_vacancy_mapper import (
    map_workday_vacancy,
)


class WorkdaySourceAdapter:
    def __init__(self, client: WorkdayCxsClient | None = None) -> None:
        self._client = client or WorkdayCxsClient()

    async def close(self) -> None:
        await self._client.close()

    async def retrieve(self, source_config: Mapping[str, Any]) -> ATSAdapterResult:
        listing = await self._client.list_jobs(source_config)
        host = f"{source_config['host_prefix']}.myworkdayjobs.com"
        site = source_config["site"]
        semaphore = asyncio.Semaphore(3)

        async def retrieve_one(job: dict[str, Any]):
            async with semaphore:
                path = job.get("externalPath")
                if not isinstance(path, str):
                    return None, "Workday posting has no externalPath."
                detail = await self._client.get_detail(source_config, path)
                if detail.posting is None:
                    return None, detail.detail or "Workday detail was unavailable."
                try:
                    return map_workday_vacancy(job, detail.posting, host, site), None
                except (KeyError, TypeError, ValueError) as error:
                    return None, str(error)

        results = await asyncio.gather(*(retrieve_one(job) for job in listing.postings))
        vacancies = []
        seen = set()
        errors = []
        for vacancy, error in results:
            if error:
                errors.append(error)
            elif vacancy.external_job_id in seen:
                errors.append("Duplicate Workday vacancy identifier.")
            else:
                seen.add(vacancy.external_job_id)
                vacancies.append(vacancy)
        complete = listing.complete and not errors
        outcome = listing.outcome
        if errors and outcome in {"success", "empty"}:
            outcome = "partial"
        detail = listing.detail
        if errors:
            detail = f"{len(errors)} Workday postings could not be normalized or detailed."
        return ATSAdapterResult(
            outcome, vacancies, listing.pages_fetched, complete, detail,
            total_vacancies=listing.total,
        )
