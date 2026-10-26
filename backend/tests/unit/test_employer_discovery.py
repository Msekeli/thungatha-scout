"""Offline unit tests for bounded employer discovery."""
import unittest
from datetime import timezone

from app.application.employer_discovery import (
    DEFAULT_QUERIES,
    run_discovery,
)


class FakeSearchProvider:
    def __init__(self, results_by_query):
        self.results_by_query = results_by_query
        self.calls = []

    def search(self, query, *, limit, region):
        self.calls.append((query, limit, region))
        result = self.results_by_query[query]
        if isinstance(result, Exception):
            raise result
        return result


class EmployerDiscoveryTests(unittest.TestCase):
    def test_default_queries_are_company_first_and_bounded(self):
        self.assertLessEqual(len(DEFAULT_QUERIES), 20)
        self.assertTrue(all("Cape Town" in query for query in DEFAULT_QUERIES))
        self.assertFalse(any(
            term in query.lower()
            for query in DEFAULT_QUERIES
            for term in ("software engineer", "developer", "data analyst")
        ))

    def test_custom_queries_cannot_expand_geographic_scope(self):
        with self.assertRaises(ValueError):
            run_discovery(FakeSearchProvider({}), queries=("Johannesburg employers",))

    def test_results_remain_unresolved_and_retain_search_evidence(self):
        query = DEFAULT_QUERIES[0]
        provider = FakeSearchProvider({query: [{
            "title": "Example Careers",
            "href": "https://example.org/careers?utm_source=search",
            "body": "Join our team in Cape Town",
        }]})
        report = run_discovery(provider, queries=(query,))

        self.assertEqual(report.status, "success_with_results")
        self.assertEqual(len(report.candidates), 1)
        candidate = report.candidates[0]
        self.assertIsNone(candidate.display_name)
        self.assertIsNone(candidate.official_website_url)
        self.assertIsNone(candidate.official_careers_url)
        self.assertEqual(candidate.identity_status.value, "unresolved")
        self.assertEqual(len(candidate.evidence), 1)
        self.assertEqual(candidate.evidence[0].query, query)
        self.assertEqual(candidate.evidence[0].observed_at.tzinfo, timezone.utc)

    def test_duplicate_urls_merge_evidence_across_queries(self):
        first, second = DEFAULT_QUERIES[:2]
        provider = FakeSearchProvider({
            first: [{"title": "Example", "href": "https://example.org/about"}],
            second: [{"title": "Example", "href": "https://example.org/about"}],
        })
        report = run_discovery(provider, queries=(first, second))

        self.assertEqual(len(report.candidates), 1)
        self.assertEqual(len(report.candidates[0].evidence), 2)

    def test_failed_query_is_not_reported_as_empty(self):
        query = DEFAULT_QUERIES[0]
        provider = FakeSearchProvider({query: TimeoutError("provider timed out")})
        report = run_discovery(provider, queries=(query,))

        self.assertEqual(report.status, "discovery_failed")
        self.assertEqual(report.query_reports[0].run.outcome.value, "request_failed")

    def test_partial_failure_is_visible_alongside_success(self):
        first, second = DEFAULT_QUERIES[:2]
        provider = FakeSearchProvider({
            first: [{"title": "Example", "href": "https://example.org"}],
            second: RuntimeError("search backend unavailable"),
        })
        report = run_discovery(provider, queries=(first, second))

        self.assertEqual(report.status, "partial")
        self.assertEqual(len(report.candidates), 1)
        self.assertEqual(
            report.query_reports[1].run.outcome.value, "request_failed"
        )

    def test_malformed_results_are_counted_not_promoted(self):
        query = DEFAULT_QUERIES[0]
        provider = FakeSearchProvider({query: [
            {"title": "", "href": "javascript:alert(1)"},
            {"title": "Valid lead", "href": "https://example.org"},
        ]})
        report = run_discovery(provider, queries=(query,))

        self.assertEqual(len(report.candidates), 1)
        self.assertEqual(report.query_reports[0].discarded_result_count, 1)

    def test_query_and_result_limits_are_enforced(self):
        query = DEFAULT_QUERIES[0]
        provider = FakeSearchProvider({query: []})
        with self.assertRaises(ValueError):
            run_discovery(provider, queries=(query,), max_results_per_query=11)
        with self.assertRaises(ValueError):
            run_discovery(provider, queries=())


if __name__ == "__main__":
    unittest.main()
