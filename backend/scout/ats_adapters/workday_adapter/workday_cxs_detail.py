from collections.abc import Mapping
from typing import Any

import httpx

from scout.ats_adapters.workday_adapter.workday_config import workday_cxs_base_url
from scout.ats_adapters.workday_adapter.workday_contracts import WorkdayDetailResult
from scout.ats_adapters.workday_adapter.workday_response_mapper import (
    map_detail_response,
)


MAX_DETAIL_BYTES = 3_000_000


async def retrieve_workday_detail(
    client: httpx.AsyncClient,
    config: Mapping[str, Any],
    external_path: str,
) -> WorkdayDetailResult:
    base = workday_cxs_base_url(config)
    if not valid_external_path(external_path):
        return WorkdayDetailResult(
            "malformed", None, "Workday externalPath is invalid."
        )
    try:
        response = await client.get(base + external_path)
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


def valid_external_path(value: str) -> bool:
    return (
        isinstance(value, str)
        and value.startswith("/")
        and not value.startswith("//")
        and ".." not in value.split("/")
    )
