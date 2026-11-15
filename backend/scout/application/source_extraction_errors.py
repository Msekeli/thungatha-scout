class SourceNotFoundError(LookupError):
    """Raised when an extraction references an unknown source."""


class UnsupportedAdapterError(ValueError):
    """Raised when a source references an unavailable adapter."""
