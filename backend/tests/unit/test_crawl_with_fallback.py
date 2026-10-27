"""Offline tests for primary/fallback crawler selection."""
import unittest

from diagnostics.crawl_with_fallback import classify_outcome, needs_fallback


class PrimaryFallbackSelectionTests(unittest.TestCase):
    def test_fallback_runs_when_primary_found_no_jobs(self):
        self.assertTrue(needs_fallback({"status": "search_control_not_found", "jobs": []}))

    def test_fallback_runs_for_empty_results(self):
        self.assertTrue(needs_fallback({"status": "no_jobs_detected", "job_count": 0}))

    def test_fallback_is_skipped_when_primary_found_jobs(self):
        self.assertFalse(needs_fallback({"status": "jobs_in_visible_html", "jobs": [{"title": "Engineer"}]}))

    def test_fallback_is_skipped_when_primary_job_count_is_positive(self):
        self.assertFalse(needs_fallback({"status": "jobs_via_network_json", "job_count": 2}))


    def test_classifies_primary_vacancy_records(self):
        self.assertEqual(
            classify_outcome({"jobs": [{"title": "Engineer"}]}, None),
            "primary_found_jobs",
        )

    def test_classifies_fallback_candidates(self):
        self.assertEqual(
            classify_outcome(
                {"jobs": [], "status": "search_control_not_found"},
                {"vacancy_candidates": [{"title": "Engineer"}]},
            ),
            "fallback_found_vacancy_candidates",
        )

    def test_distinguishes_email_recruitment(self):
        self.assertEqual(
            classify_outcome(
                {"jobs": [], "status": "unresolved",
                 "pages": [{"application_emails": ["careers@example.com"]}]},
                None,
            ),
            "email_based_recruitment",
        )

    def test_distinguishes_no_jobs_from_access_failure(self):
        self.assertEqual(
            classify_outcome({"jobs": [], "status": "page_says_no_jobs"}, None),
            "successful_no_vacancy_evidence",
        )
        self.assertEqual(
            classify_outcome({"jobs": [], "status": "blocked"}, None),
            "blocked_or_inaccessible",
        )


if __name__ == "__main__":
    unittest.main()
