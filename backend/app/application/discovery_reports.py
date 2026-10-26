"""Small report models shared by discovery and CLI output."""
from datetime import datetime
from pydantic import BaseModel
from app.domain.discovery import DiscoveryRunResult, EmployerCandidate


class DiscoveryQueryReport(BaseModel):
    query: str
    run: DiscoveryRunResult
    raw_result_count: int = 0
    discarded_result_count: int = 0
    excluded_aggregator_count: int = 0


class DiscoveryBatchReport(BaseModel):
    started_at: datetime
    finished_at: datetime
    status: str
    query_reports: list[DiscoveryQueryReport]
    candidates: list[EmployerCandidate]
    coverage_note: str = (
        "Search coverage is incomplete by design; results are leads, not verified "
        "employers or proof of Cape Town presence."
    )
