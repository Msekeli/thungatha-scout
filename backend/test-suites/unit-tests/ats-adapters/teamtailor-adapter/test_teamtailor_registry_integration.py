from uuid import uuid4

from scout.application.employer_contracts import EmployerSourceCreate
from scout.application.source_extraction_service import SourceExtractionService
from scout.application.source_preview_service import SourcePreviewService
from scout.registry_loader import validate_source_config


def test_teamtailor_source_configuration_is_registered() -> None:
    config = {"careers_url": "https://root.teamtailor.com/jobs"}
    validate_source_config("teamtailor", config)
    payload = EmployerSourceCreate(
        employer_id=uuid4(),
        adapter_key="teamtailor",
        source_url=config["careers_url"],
        normalized_url=config["careers_url"],
        adapter_config=config,
    )
    assert payload.adapter_key == "teamtailor"


def test_shared_services_register_teamtailor_adapter() -> None:
    factory = lambda: None
    extraction = SourceExtractionService(connection_factory=factory)
    preview = SourcePreviewService(connection_factory=factory)
    assert "teamtailor" in extraction._adapter_factories
    assert "teamtailor" in preview._adapter_factories
