from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.workday_adapter.workday_config import (
    MAX_LIST_BYTES,
    PAGE_SIZE,
    RESULT_CAP,
    workday_cxs_base_url,
)
from scout.ats_adapters.workday_adapter.workday_contracts import WorkdayListResult
from scout.ats_adapters.workday_adapter.workday_response_mapper import (
    map_list_response,
)


async def retrieve_workday_listing(
    client: httpx.AsyncClient, config: Mapping[str, Any]
) -> WorkdayListResult:
    base = workday_cxs_base_url(config)
    host = f"{config['host_prefix']}.myworkdayjobs.com"
    postings: list[dict[str, Any]] = []
    total = offset = pages = 0
    while offset < min(total or PAGE_SIZE, RESULT_CAP):
        try:
            response = await client.post(
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
        if len(page.postings) > PAGE_SIZE or (not page.postings and offset < total):
            return WorkdayListResult(
                "partial",
                postings,
                total,
                pages,
                False,
                "Workday returned an invalid page size or an empty page before total.",
            )
        postings.extend(page.postings)
        offset += PAGE_SIZE
    if total > RESULT_CAP or len(postings) != total:
        return WorkdayListResult(
            "partial",
            postings,
            total,
            pages,
            False,
            "Workday listing is incomplete or reached its cap.",
        )
    return WorkdayListResult(
        "success" if postings else "empty", postings, total, pages, True
    )
