from collections.abc import Callable

from scout.ats_adapters.ats_adapter_contracts import ATSAdapter
from scout.ats_adapters.greenhouse_adapter.greenhouse_source_adapter import (
    GreenhouseSourceAdapter,
)
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter
from scout.ats_adapters.teamtailor_adapter.teamtailor_source_adapter import (
    TeamtailorSourceAdapter,
)
from scout.ats_adapters.workable_adapter.workable_source_adapter import (
    WorkableSourceAdapter,
)
from scout.ats_adapters.workday_adapter.workday_source_adapter import (
    WorkdaySourceAdapter,
)


def create_source_adapter_factories() -> dict[str, Callable[[], ATSAdapter]]:
    return {
        "greenhouse": GreenhouseSourceAdapter,
        "lever": LeverSourceAdapter,
        "teamtailor": TeamtailorSourceAdapter,
        "workable": WorkableSourceAdapter,
        "workday": WorkdaySourceAdapter,
    }
