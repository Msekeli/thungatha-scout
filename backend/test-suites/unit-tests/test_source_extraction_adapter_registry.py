from scout.application.source_extraction_service import SourceExtractionService
from scout.application.source_preview_service import SourcePreviewService
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter
from scout.ats_adapters.workable_adapter.workable_source_adapter import (
    WorkableSourceAdapter,
)
from scout.ats_adapters.workday_adapter.workday_source_adapter import (
    WorkdaySourceAdapter,
)


def test_lever_is_registered_in_the_shared_extraction_service() -> None:
    service = SourceExtractionService(connection_factory=lambda: None)
    assert service._adapter_factories["lever"] is LeverSourceAdapter


def test_workable_is_registered_in_both_services() -> None:
    extraction = SourceExtractionService(connection_factory=lambda: None)
    preview = SourcePreviewService(connection_factory=lambda: None)
    assert extraction._adapter_factories["workable"] is WorkableSourceAdapter
    assert preview._adapter_factories["workable"] is WorkableSourceAdapter


def test_workday_is_registered_in_both_services() -> None:
    extraction = SourceExtractionService(connection_factory=lambda: None)
    preview = SourcePreviewService(connection_factory=lambda: None)
    assert extraction._adapter_factories["workday"] is WorkdaySourceAdapter
    assert preview._adapter_factories["workday"] is WorkdaySourceAdapter
