"""Backward-compatible exports for the shared source extraction service."""

from scout.application.source_extraction_service import (
    SourceExtractionService as GreenhouseExtractionService,
)
from scout.application.source_extraction_service import (
    SourceNotFoundError,
    UnsupportedAdapterError,
)

__all__ = [
    "GreenhouseExtractionService",
    "SourceNotFoundError",
    "UnsupportedAdapterError",
]
