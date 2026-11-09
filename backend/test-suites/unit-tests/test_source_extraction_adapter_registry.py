from scout.application.source_extraction_service import SourceExtractionService
from scout.ats_adapters.lever_adapter.lever_source_adapter import LeverSourceAdapter


def test_lever_is_registered_in_the_shared_extraction_service() -> None:
    service = SourceExtractionService(connection_factory=lambda: None)

    assert service._adapter_factories["lever"] is LeverSourceAdapter
