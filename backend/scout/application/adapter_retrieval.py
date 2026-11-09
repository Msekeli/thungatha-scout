from collections.abc import Mapping
from typing import Any

from scout.ats_adapters.ats_adapter_contracts import (
    ATSAdapter,
    ATSAdapterResult,
)


async def retrieve_adapter_result(
    adapter: ATSAdapter, source_config: Mapping[str, Any]
) -> ATSAdapterResult:
    try:
        result = await adapter.retrieve(source_config)
    except ValueError as exception:
        result = ATSAdapterResult(
            "malformed", [], 0, False, f"Invalid adapter configuration: {exception}"
        )
    except Exception as exception:
        result = ATSAdapterResult(
            "transient_failure",
            [],
            0,
            False,
            f"Adapter retrieval failed ({type(exception).__name__}): {exception}",
        )
    try:
        await adapter.close()
    except Exception as exception:
        if result.outcome in ("success", "empty"):
            return ATSAdapterResult(
                "transient_failure",
                [],
                result.pages_fetched,
                False,
                f"Adapter cleanup failed ({type(exception).__name__}): {exception}",
            )
    return result
