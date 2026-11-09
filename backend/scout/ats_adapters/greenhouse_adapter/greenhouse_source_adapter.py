from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from .greenhouse_adapter import GreenhouseAdapter
from .greenhouse_vacancy_mapper import map_greenhouse_job


class GreenhouseSourceAdapter:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._adapter = GreenhouseAdapter(client)

    async def retrieve(self, source_config: Mapping[str, Any]) -> ATSAdapterResult:
        slug = source_config.get("slug")
        if not isinstance(slug, str) or not slug.strip():
            raise ValueError("Greenhouse source configuration requires a slug.")
        result = await self._adapter.retrieve(slug)
        vacancies = [map_greenhouse_job(job) for job in result.jobs]
        return ATSAdapterResult(
            outcome=result.outcome,
            vacancies=vacancies,
            pages_fetched=result.pages_fetched,
            complete=result.complete,
            detail=result.detail,
            total_vacancies=result.total_jobs,
        )

    async def close(self) -> None:
        await self._adapter.close()
