"""Offline unit tests for bounded employer discovery."""
import unittest
from datetime import timezone
from types import SimpleNamespace
from unittest.mock import patch

from app.application.employer_discovery import (
    DEFAULT_QUERIES,
    DDGSSearchProvider,
    SearchProviderError,
    compare_search_backends,
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

    def test_successful_empty_response_is_reported_as_empty(self):
        query = DEFAULT_QUERIES[0]
        report = run_discovery(FakeSearchProvider({query: []}), queries=(query,))

        self.assertEqual(report.status, "success_empty")
        self.assertEqual(report.query_reports[0].run.outcome.value, "success_empty")

    def test_known_job_aggregators_are_excluded_but_official_leads_remain(self):
        query = DEFAULT_QUERIES[0]
        provider = FakeSearchProvider({query: [
            {
                "title": "Indeed Cape Town jobs",
                "href": "https://za.indeed.com/available-vacancies-jobs-in-cape-town",
                "body": "Vacancies in Cape Town",
            },
            {
                "title": "Impact careers",
                "href": "https://impact.com/careers/cape-town-jobs/",
                "body": "Join our software company in Cape Town",
            },
        ]})
        report = run_discovery(provider, queries=(query,))

        self.assertEqual(len(report.candidates), 1)
        query_report = report.query_reports[0]
        self.assertEqual(query_report.raw_result_count, 2)
        self.assertEqual(query_report.excluded_aggregator_count, 1)
        self.assertEqual(query_report.discarded_result_count, 0)
        excerpt = report.candidates[0].evidence[0].excerpt
        self.assertIn("Title: Impact careers", excerpt)
        self.assertIn("Join our software company", excerpt)

    def test_backend_comparison_runs_each_backend_independently_with_same_queries(self):
        calls = []

        def fake_run_discovery(*, provider, queries, max_results_per_query, region):
            calls.append((provider.backends, queries, max_results_per_query, region))
            return SimpleNamespace(
                status="success_with_results",
                query_reports=[
                    SimpleNamespace(
                        run=SimpleNamespace(outcome=SimpleNamespace(value="success_with_results")),
                        raw_result_count=2,
                        excluded_aggregator_count=1,
                        discarded_result_count=0,
                        query=query,
                    )
                    for query in queries
                ],
                candidates=[
                    SimpleNamespace(
                        observed_url=f"https://example-{provider.backends[0]}.org/careers",
                        evidence=[SimpleNamespace(query=queries[0], excerpt="Title: Careers")],
                    )
                ],
            )

        queries = DEFAULT_QUERIES[:2]
        with patch("app.application.employer_discovery.run_discovery", side_effect=fake_run_discovery):
            report = compare_search_backends(
                backends=("bing", "brave"),
                queries=queries,
                max_results_per_query=4,
                region="za-en",
            )

        self.assertEqual([call[0] for call in calls], [("bing",), ("brave",)])
        self.assertTrue(all(call[1] == queries for call in calls))
        self.assertTrue(all(call[2:] == (4, "za-en") for call in calls))
        self.assertEqual([item["backend"] for item in report["backends"]], ["bing", "brave"])
        self.assertTrue(all(item["failed_queries"] == 0 for item in report["backends"]))
        self.assertTrue(all(item["distinct_candidate_urls"] == 1 for item in report["backends"]))
    def test_ddgs_provider_falls_back_after_backend_error(self):
        calls = []
        responses = {
            "brave": RuntimeError("No results found."),
            "duckduckgo": [{"title": "Impact careers", "href": "https://impact.com/careers"}],
        }

        class FakeClient:
            def __init__(self, timeout):
                self.timeout = timeout

            def text(self, query, **kwargs):
                backend = kwargs["backend"]
                calls.append(backend)
                response = responses[backend]
                if isinstance(response, Exception):
                    raise response
                return response

        provider = DDGSSearchProvider(
            backends=("brave", "duckduckgo"),
            client_factory=FakeClient,
        )
        results = provider.search("Cape Town careers", limit=5, region="za-en")

        self.assertEqual(calls, ["brave", "duckduckgo"])
        self.assertEqual(len(results), 1)

    def test_ddgs_all_backend_errors_remain_provider_failure(self):
        class FakeClient:
            def __init__(self, timeout):
                pass

            def text(self, query, **kwargs):
                raise RuntimeError("No results found.")

        provider = DDGSSearchProvider(
            backends=("brave", "duckduckgo"),
            client_factory=FakeClient,
        )
        with self.assertRaises(SearchProviderError):
            provider.search("Cape Town careers", limit=5, region="za-en")

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
