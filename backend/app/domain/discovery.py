"""Typed discovery records and explicit outcomes for employer discovery."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from enum import Enum
from urllib.parse import urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class DiscoveryOutcome(str, Enum):
    SUCCESS_WITH_RESULTS = "success_with_results"
    SUCCESS_EMPTY = "success_empty"
    REQUEST_FAILED = "request_failed"
    DISCOVERY_FAILED = "discovery_failed"


class IdentityStatus(str, Enum):
    CANDIDATE = "candidate"
    VERIFIED = "verified"
    UNRESOLVED = "unresolved"


class OrganizationType(str, Enum):
    DIRECT_EMPLOYER = "direct_employer"
    RECRUITMENT_AGENCY = "recruitment_agency"
    STAFFING_COMPANY = "staffing_company"
    HYBRID = "hybrid"
    OTHER = "other"
    UNRESOLVED = "unresolved"


class ReviewState(str, Enum):
    DISCOVERED = "discovered"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"
    INACTIVE = "inactive"


class DiscoveryEvidence(BaseModel):
    """One traceable observation supporting a candidate or a decision."""
    model_config = ConfigDict(extra="forbid")

    method: str = Field(min_length=1, max_length=100)
    query: str | None = Field(default=None, max_length=1000)
    observed_url: HttpUrl
    observed_at: datetime
    reference_url: HttpUrl | None = None
    excerpt: str | None = Field(default=None, max_length=2000)
    note: str | None = Field(default=None, max_length=2000)

    @field_validator("observed_at")
    @classmethod
    def require_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("observed_at must be timezone-aware")
        return value.astimezone(timezone.utc)


class EmployerCandidate(BaseModel):
    """A possible employer; fields remain uncertain until evidence supports them."""
    model_config = ConfigDict(extra="forbid")

    candidate_id: str = Field(min_length=1, max_length=80)
    display_name: str | None = Field(default=None, max_length=250)
    observed_url: HttpUrl
    official_website_url: HttpUrl | None = None
    official_careers_url: HttpUrl | None = None
    identity_status: IdentityStatus = IdentityStatus.UNRESOLVED
    organization_type: OrganizationType = OrganizationType.UNRESOLVED
    review_state: ReviewState = ReviewState.DISCOVERED
    location_evidence: list[DiscoveryEvidence] = Field(default_factory=list)
    evidence: list[DiscoveryEvidence] = Field(min_length=1)
    first_seen_at: datetime
    last_checked_at: datetime

    @field_validator("first_seen_at", "last_checked_at")
    @classmethod
    def require_utc_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def verify_identity_has_evidence(self) -> "EmployerCandidate":
        if self.identity_status == IdentityStatus.VERIFIED:
            if self.official_website_url is None:
                raise ValueError("verified identity requires an official website URL")
        return self


class DiscoveryRunResult(BaseModel):
    """Summary of one search operation, preserving success and failure separately."""
    model_config = ConfigDict(extra="forbid")

    outcome: DiscoveryOutcome
    method: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=1000)
    started_at: datetime
    finished_at: datetime
    candidates: list[EmployerCandidate] = Field(default_factory=list)
    error_code: str | None = Field(default=None, max_length=100)
    error_message: str | None = Field(default=None, max_length=1000)

    @field_validator("started_at", "finished_at")
    @classmethod
    def require_utc_aware_time(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("timestamps must be timezone-aware")
        return value.astimezone(timezone.utc)

    @model_validator(mode="after")
    def outcome_matches_payload(self) -> "DiscoveryRunResult":
        if self.finished_at < self.started_at:
            raise ValueError("finished_at cannot be earlier than started_at")
        if self.outcome == DiscoveryOutcome.SUCCESS_WITH_RESULTS and not self.candidates:
            raise ValueError("success_with_results requires at least one candidate")
        if self.outcome == DiscoveryOutcome.SUCCESS_EMPTY and self.candidates:
            raise ValueError("success_empty cannot contain candidates")
        if self.outcome in {DiscoveryOutcome.REQUEST_FAILED, DiscoveryOutcome.DISCOVERY_FAILED} and not (self.error_code or self.error_message):
            raise ValueError("failed outcomes require an error code or message")
        if self.outcome in {DiscoveryOutcome.SUCCESS_WITH_RESULTS, DiscoveryOutcome.SUCCESS_EMPTY} and (self.error_code or self.error_message):
            raise ValueError("successful outcomes cannot carry failure details")
        return self


def stable_candidate_id(observed_url: str, verified_employer_domain: str | None = None) -> str:
    """Deterministic ID; an unverified ATS token is never treated as employer identity."""
    if verified_employer_domain:
        host = verified_employer_domain.strip().lower().rstrip(".")
        if not host or "/" in host or "://" in host:
            raise ValueError("verified_employer_domain must be a hostname")
        identity = f"verified-domain:{host}"
    else:
        parsed = urlsplit(observed_url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("observed_url must be an absolute HTTP(S) URL")
        normalized = urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), parsed.path.rstrip("/") or "/", "", ""))
        identity = f"observation:{normalized}"
    digest = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:32]
    return f"cand_{digest}"
