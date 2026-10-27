"""Offline tests for primary/fallback crawler selection."""
import unittest

from diagnostics.crawl_with_fallback import needs_fallback


class PrimaryFallbackSelectionTests(unittest.TestCase):
    def test_fallback_runs_when_primary_found_no_jobs(self):
        self.assertTrue(needs_fallback({"status": "search_control_not_found", "jobs": []}))

    def test_fallback_runs_for_empty_results(self):
        self.assertTrue(needs_fallback({"status": "no_jobs_detected", "job_count": 0}))

    def test_fallback_is_skipped_when_primary_found_jobs(self):
        self.assertFalse(needs_fallback({"status": "jobs_in_visible_html", "jobs": [{"title": "Engineer"}]}))

    def test_fallback_is_skipped_when_primary_job_count_is_positive(self):
        self.assertFalse(needs_fallback({"status": "jobs_via_network_json", "job_count": 2}))


if __name__ == "__main__":
    unittest.main()
