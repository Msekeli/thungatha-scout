from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.ats_adapters.lever_adapter.lever_postings_client import (
    LeverPostingsClient,
)
from scout.ats_adapters.lever_adapter.lever_vacancy_mapper import map_lever_posting


class LeverSourceAdapter:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = LeverPostingsClient(client)

    async def retrieve(self, source_config: Mapping[str, Any]) -> ATSAdapterResult:
        slug = source_config.get("slug")
        region = source_config.get("region")
        if not isinstance(slug, str) or not isinstance(region, str):
            raise TypeError(
                "Lever source configuration requires string slug and region."
            )
        result = await self._client.retrieve(slug, region)
        vacancies = []
        mapping_errors = 0
        for job in result.jobs:
            try:
                vacancies.append(map_lever_posting(job))
            except (KeyError, TypeError, ValueError):
                mapping_errors += 1
        outcome = result.outcome
        complete = result.complete
        detail = result.detail
        if mapping_errors:
            if outcome in {"success", "empty"}:
                outcome = "partial"
            complete = False
            detail = f"{mapping_errors} Lever postings failed normalization."
        return ATSAdapterResult(
            outcome=outcome,
            vacancies=vacancies,
            pages_fetched=result.pages_fetched,
            complete=complete,
            detail=detail,
            total_vacancies=len(result.jobs) if complete else None,
        )

    async def close(self) -> None:
        await self._client.close()
