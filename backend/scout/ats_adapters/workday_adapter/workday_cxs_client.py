from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.workday_adapter.workday_config import workday_cxs_base_url
from scout.ats_adapters.workday_adapter.workday_contracts import (
    WorkdayDetailResult,
    WorkdayListResult,
)
from scout.ats_adapters.workday_adapter.workday_response_mapper import (
    map_detail_response,
    map_list_response,
)


PAGE_SIZE = 20
RESULT_CAP = 2000
MAX_LIST_BYTES = 5_000_000
MAX_DETAIL_BYTES = 3_000_000


class WorkdayCxsClient:
    def __init__(self, client: httpx.AsyncClient | None = None) -> None:
        self._client = client or httpx.AsyncClient(
            timeout=20.0,
            follow_redirects=True,
            max_redirects=3,
            headers={"Accept": "application/json"},
        )
        self._owns_client = client is None

    async def close(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def list_jobs(self, config: Mapping[str, Any]) -> WorkdayListResult:
        base = workday_cxs_base_url(config)
        host = f"{config['host_prefix']}.myworkdayjobs.com"
        postings: list[dict[str, Any]] = []
        total = offset = pages = 0
        while offset < min(total or PAGE_SIZE, RESULT_CAP):
            try:
                response = await self._client.post(
                    f"{base}/jobs",
                    json={
                        "appliedFacets": {},
                        "limit": PAGE_SIZE,
                        "offset": offset,
                        "searchText": "",
                    },
                )
            except httpx.TimeoutException:
                return WorkdayListResult(
                    "transient_failure",
                    postings,
                    total,
                    pages,
                    False,
                    "Workday listing timed out.",
                )
            except httpx.TransportError:
                return WorkdayListResult(
                    "transient_failure",
                    postings,
                    total,
                    pages,
                    False,
                    "Workday listing transport failed.",
                )
            pages += 1
            if response.url.host != host or len(response.content) > MAX_LIST_BYTES:
                return WorkdayListResult(
                    "malformed",
                    postings,
                    total,
                    pages,
                    False,
                    "Workday listing host or size is invalid.",
                )
            page = map_list_response(response)
            if not page.complete:
                return WorkdayListResult(
                    page.outcome, postings, total, pages, False, page.detail
                )
            total = page.total
            if len(page.postings) > PAGE_SIZE:
                return WorkdayListResult(
                    "partial",
                    postings,
                    total,
                    pages,
                    False,
                    "Workday exceeded the 20-item page size.",
                )
            if not page.postings and offset < total:
                return WorkdayListResult(
                    "partial",
                    postings,
                    total,
                    pages,
                    False,
                    "Workday returned an empty page before total.",
                )
            postings.extend(page.postings)
            offset += PAGE_SIZE
        if total > RESULT_CAP:
            return WorkdayListResult(
                "partial",
                postings,
                total,
                pages,
                False,
                "Workday CXS result cap reached at 2,000.",
            )
        if len(postings) != total:
            return WorkdayListResult(
                "partial",
                postings,
                total,
                pages,
                False,
                "Workday listing count does not match total.",
            )
        outcome = "success" if postings else "empty"
        return WorkdayListResult(outcome, postings, total, pages, True)

    async def get_detail(
        self, config: Mapping[str, Any], external_path: str
    ) -> WorkdayDetailResult:
        base = self._base_url(config)
        if (
            not isinstance(external_path, str)
            or not external_path.startswith("/")
            or external_path.startswith("//")
            or ".." in external_path.split("/")
        ):
            return WorkdayDetailResult(
                "malformed", None, "Workday externalPath is invalid."
            )
        try:
            response = await self._client.get(base + external_path)
        except httpx.TimeoutException:
            return WorkdayDetailResult(
                "transient_failure", None, "Workday detail request timed out."
            )
        except httpx.TransportError:
            return WorkdayDetailResult(
                "transient_failure", None, "Workday detail transport failed."
            )
        host = f"{config['host_prefix']}.myworkdayjobs.com"
        if response.url.host != host or len(response.content) > MAX_DETAIL_BYTES:
            return WorkdayDetailResult(
                "malformed", None, "Workday detail host or size is invalid."
            )
        return map_detail_response(response)
