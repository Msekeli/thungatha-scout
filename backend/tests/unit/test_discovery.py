"""Unit tests for the M1-C01 discovery contract."""
import unittest
from datetime import datetime, timedelta, timezone

from pydantic import ValidationError

from app.domain.discovery import (
    DiscoveryEvidence, DiscoveryOutcome, DiscoveryRunResult,
    EmployerCandidate, IdentityStatus, stable_candidate_id,
)

NOW = datetime(2026, 10, 26, 10, 0, tzinfo=timezone.utc)


def make_evidence():
    return DiscoveryEvidence(
        method="search",
        query="companies in Cape Town official careers",
        observed_url="https://example.org/about",
        observed_at=NOW,
        reference_url="https://example.org/careers",
        note="Example test evidence",
    )


def make_candidate():
    return EmployerCandidate(
        candidate_id=stable_candidate_id("https://example.org/about"),
        display_name="Example Organisation",
        observed_url="https://example.org/about",
        identity_status=IdentityStatus.CANDIDATE,
        evidence=[make_evidence()],
        first_seen_at=NOW,
        last_checked_at=NOW,
    )


class DiscoveryOutcomeTests(unittest.TestCase):
    def make_result(self, outcome, **kwargs):
        values = dict(
            outcome=outcome, method="search", query="Cape Town employers",
            started_at=NOW, finished_at=NOW + timedelta(seconds=1),
        )
        values.update(kwargs)
        return DiscoveryRunResult(**values)

    def test_successful_empty_result_is_valid_and_distinct(self):
        result = self.make_result(DiscoveryOutcome.SUCCESS_EMPTY)
        self.assertEqual(result.outcome, DiscoveryOutcome.SUCCESS_EMPTY)
        self.assertEqual(result.candidates, [])

    def test_success_with_results_requires_candidates(self):
        with self.assertRaises(ValidationError):
            self.make_result(DiscoveryOutcome.SUCCESS_WITH_RESULTS)

    def test_success_with_results_accepts_candidate(self):
        result = self.make_result(DiscoveryOutcome.SUCCESS_WITH_RESULTS, candidates=[make_candidate()])
        self.assertEqual(len(result.candidates), 1)

    def test_empty_success_cannot_hide_candidates(self):
        with self.assertRaises(ValidationError):
            self.make_result(DiscoveryOutcome.SUCCESS_EMPTY, candidates=[make_candidate()])

    def test_request_failure_requires_error_and_is_not_empty_success(self):
        with self.assertRaises(ValidationError):
            self.make_result(DiscoveryOutcome.REQUEST_FAILED)
        result = self.make_result(
            DiscoveryOutcome.REQUEST_FAILED,
            error_code="timeout", error_message="Search provider timed out",
        )
        self.assertEqual(result.outcome, DiscoveryOutcome.REQUEST_FAILED)

    def test_total_discovery_failure_is_explicit(self):
        result = self.make_result(DiscoveryOutcome.DISCOVERY_FAILED, error_code="provider_unavailable")
        self.assertEqual(result.outcome, DiscoveryOutcome.DISCOVERY_FAILED)

    def test_verified_identity_requires_official_website(self):
        with self.assertRaises(ValidationError):
            EmployerCandidate(
                candidate_id="cand_test", observed_url="https://boards.example/jobs",
                identity_status=IdentityStatus.VERIFIED, evidence=[make_evidence()],
                first_seen_at=NOW, last_checked_at=NOW,
            )

    def test_naive_timestamp_is_rejected(self):
        with self.assertRaises(ValidationError):
            DiscoveryEvidence(
                method="search", observed_url="https://example.org",
                observed_at=datetime(2026, 10, 26, 10, 0),
            )

    def test_stable_id_is_repeatable_and_tracking_independent(self):
        first = stable_candidate_id("https://example.org/about?utm_source=test#team")
        second = stable_candidate_id("https://example.org/about")
        self.assertEqual(first, second)

    def test_unverified_observation_does_not_merge_with_verified_domain(self):
        observed = stable_candidate_id("https://boards.example/company/acme")
        verified = stable_candidate_id("https://boards.example/company/acme", verified_employer_domain="acme.example")
        self.assertNotEqual(observed, verified)


if __name__ == "__main__":
    unittest.main()
