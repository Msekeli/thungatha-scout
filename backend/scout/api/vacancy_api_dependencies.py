from scout.application.source_extraction_service import SourceExtractionService


def get_extraction_service() -> SourceExtractionService:
    return SourceExtractionService()
