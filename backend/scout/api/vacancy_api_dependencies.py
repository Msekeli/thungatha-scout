from scout.application.source_extraction_service import SourceExtractionService
from scout.application.source_preview_service import SourcePreviewService


def get_extraction_service() -> SourceExtractionService:
    return SourceExtractionService()


def get_source_preview_service() -> SourcePreviewService:
    return SourcePreviewService()
