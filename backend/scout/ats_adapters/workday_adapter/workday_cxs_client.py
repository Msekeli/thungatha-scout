from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.workday_adapter.workday_contracts import (
    WorkdayDetailResult,
    WorkdayListResult,
)
from scout.ats_adapters.workday_adapter.workday_cxs_detail import (
    retrieve_workday_detail,
)
from scout.ats_adapters.workday_adapter.workday_cxs_listing import (
    retrieve_workday_listing,
)


class WorkdayCxsClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=20.0, follow_redirects=True, max_redirects=3,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def list_jobs(self, config: Mapping[str, Any]) -> WorkdayListResult:
        return await retrieve_workday_listing(self._client, config)

    async def get_detail(
        self, config: Mapping[str, Any], external_path: str
    ) -> WorkdayDetailResult:
        return await retrieve_workday_detail(self._client, config, external_path)
