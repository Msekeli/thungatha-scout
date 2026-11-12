import re
from collections.abc import Mapping
from typing import Any

import httpx

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

    def _base_url(self, config: Mapping[str, Any]) -> str:
        prefix, tenant, site = (config.get(key) for key in
                                ("host_prefix", "tenant", "site"))
        if not all(isinstance(v, str) and v for v in (prefix, tenant, site)):
            raise ValueError("Workday config requires host_prefix, tenant and site.")
        if not re.fullmatch(r"[a-z0-9-]+\.wd[0-9]+", prefix):
            raise ValueError("Workday host_prefix is invalid.")
        if prefix.split(".")[0] != tenant:
            raise ValueError("Workday host tenant does not match host_prefix.")
        if not re.fullmatch(r"[A-Za-z0-9_-]+", site):
            raise ValueError("Workday site identifier is invalid.")
        return f"https://{prefix}.myworkdayjobs.com/wday/cxs/{tenant}/{site}"

    async def list_jobs(self, config: Mapping[str, Any]) -> WorkdayListResult:
        base = self._base_url(config)
        postings: list[dict[str, Any]] = []
        total = 0
        offset = 0
        pages = 0
        while offset < min(total or PAGE_SIZE, RESULT_CAP):
            try:
                response = await self._client.post(
                    f"{base}/jobs",
                    json={"appliedFacets": {}, "limit": PAGE_SIZE,
                          "offset": offset, "searchText": ""},
                )
            except httpx.TimeoutException:
                return WorkdayListResult("transient_failure", postings, total,
                                         pages, False, "Workday listing timed out.")
            except httpx.TransportError:
                return WorkdayListResult("transient_failure", postings, total,
                                         pages, False, "Workday listing transport failed.")
            page = map_list_response(response)
            pages += 1
            if not page.complete:
                return WorkdayListResult(page.outcome, postings, total, pages,
                                         False, page.detail)
            total = page.total
            if not page.postings and offset < total:
                return WorkdayListResult("partial", postings, total, pages, False,
                                         "Workday returned an empty page before total.")
            postings.extend(page.postings)
            offset += PAGE_SIZE
        if total > RESULT_CAP:
            return WorkdayListResult("partial", postings, total, pages, False,
                                     "Workday CXS result cap reached at 2,000.")
        if len(postings) != total:
            return WorkdayListResult("partial", postings, total, pages, False,
                                     "Workday listing count does not match total.")
        return WorkdayListResult("success" if postings else "empty",
                                 postings, total, pages, True)

    async def get_detail(self, config: Mapping[str, Any],
                         external_path: str) -> WorkdayDetailResult:
        base = self._base_url(config)
        if not isinstance(external_path, str) or not external_path.startswith("/") \
                or external_path.startswith("//") or ".." in external_path.split("/"):
            return WorkdayDetailResult("malformed", None,
                                       "Workday externalPath is invalid.")
        try:
            response = await self._client.get(base + external_path)
        except httpx.TimeoutException:
            return WorkdayDetailResult("transient_failure", None,
                                       "Workday detail request timed out.")
        except httpx.TransportError:
            return WorkdayDetailResult("transient_failure", None,
                                       "Workday detail transport failed.")
        return map_detail_response(response)
