from collections.abc import Mapping
from dataclasses import replace
from typing import Any

import httpx

from scout.ats_adapters.ats_adapter_contracts import ATSAdapterResult
from scout.ats_adapters.teamtailor_adapter.teamtailor_feed_client import (
    TeamtailorFeedClient,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_url_parser import (
    parse_teamtailor_careers_url,
)
from scout.ats_adapters.teamtailor_adapter.teamtailor_vacancy_mapper import (
    map_teamtailor_job,
)


class TeamtailorSourceAdapter:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = TeamtailorFeedClient(client)
        self.channel_title: str | None = None

    async def retrieve(self, source_config: Mapping[str, Any]) -> ATSAdapterResult:
        careers_url = source_config.get("careers_url")
        if not isinstance(careers_url, str):
            raise ValueError("Teamtailor source configuration requires careers_url.")
        config, feed_url = parse_teamtailor_careers_url(careers_url)
        result = await self._client.retrieve(config["careers_url"], feed_url)
        self.channel_title = result.channel_title
        vacancies, errors = [], 0
        for job in result.jobs:
            try:
                vacancy = map_teamtailor_job(job)
                payload = dict(vacancy.raw_payload)
                payload["teamtailor_channel_title"] = self.channel_title
                vacancies.append(replace(vacancy, raw_payload=payload))
            except (KeyError, TypeError, ValueError):
                errors += 1
        outcome, complete, detail = result.outcome, result.complete, result.detail
        if errors:
            outcome = "partial" if outcome in {"success", "empty"} else outcome
            complete, detail = False, f"{errors} Teamtailor vacancies failed normalization."
        return ATSAdapterResult(
            outcome, vacancies, result.pages_fetched, complete, detail,
            len(vacancies) if complete else None,
        )

    async def close(self) -> None:
        await self._client.close()
