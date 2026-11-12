from dataclasses import dataclass, field
from typing import Any
import httpx
from scout.ats_adapters.workday_adapter.workday_config import (
    PAGE_SIZE,
    RESULT_CAP,
    workday_cxs_base_url,
)
from scout.ats_adapters.workday_adapter.workday_response_mapper import (
    map_list_response,
)


@dataclass
class ListingScanResult:
    status_code: int | None = None
    reported_total: int = 0
    postings: list[dict[str, Any]] = field(default_factory=list)
    unique_paths: set[str] = field(default_factory=set)
    pages_fetched: int = 0
    complete: bool = False
    cap_reached: bool = False
    duplicates: int = 0
    errors: list[str] = field(default_factory=list)


async def scan_workday_listing(
    client: httpx.AsyncClient, config: dict[str, Any]
) -> ListingScanResult:
    base = workday_cxs_base_url(config)
    res = ListingScanResult()
    offset = 0
    while offset < min(res.reported_total or PAGE_SIZE, RESULT_CAP):
        try:
            resp = await client.post(
                f"{base}/jobs",
                json={
                    "appliedFacets": {},
                    "limit": PAGE_SIZE,
                    "offset": offset,
                    "searchText": "",
                },
            )
        except Exception as exc:
            res.errors.append(f"HTTP transport failed at offset {offset}: {exc}")
            break
        if res.status_code is None:
            res.status_code = resp.status_code
        res.pages_fetched += 1
        page = map_list_response(resp)
        if not page.complete:
            res.errors.append(page.detail or f"Page at {offset} failed.")
            break
        if offset == 0 or page.total > 0:
            res.reported_total = page.total
        for job in page.postings:
            path = job.get("externalPath")
            if not isinstance(path, str) or not path:
                res.errors.append(f"Posting at offset {offset} has no externalPath.")
                continue
            if path in res.unique_paths:
                res.duplicates += 1
                continue
            res.unique_paths.add(path)
            res.postings.append(job)
        if len(page.postings) < PAGE_SIZE:
            break
        offset += PAGE_SIZE
    res.cap_reached = res.reported_total > RESULT_CAP
    res.complete = (
        len(res.unique_paths) == res.reported_total
        and not res.errors
        and not res.cap_reached
    )
    return res
