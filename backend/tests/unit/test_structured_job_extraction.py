"""Offline tests for Schema.org JobPosting extraction."""
import json
import unittest

from app.application.structured_job_extraction import extract_job_postings


class StructuredJobExtractionTests(unittest.TestCase):
    def page(self, payload):
        return '<html><script type="application/ld+json">' + json.dumps(payload) + '</script></html>'

    def test_extracts_job_posting_and_keeps_provenance(self):
        html = self.page({
            "@context": "https://schema.org",
            "@type": "JobPosting",
            "title": "Software Engineer",
            "url": "/jobs/123",
            "description": "Build services",
            "datePosted": "2026-10-20",
            "employmentType": "FULL_TIME",
            "jobLocation": {"address": {
                "addressLocality": "Cape Town", "addressCountry": "ZA"
            }},
        })
        jobs = extract_job_postings(html, "https://example.org/careers", "Example Co")
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["title"], "Software Engineer")
        self.assertEqual(jobs[0]["job_url"], "https://example.org/jobs/123")
        self.assertEqual(jobs[0]["locations"], ["Cape Town, ZA"])
        self.assertEqual(jobs[0]["source_page_url"], "https://example.org/careers")
        self.assertEqual(jobs[0]["company"], "Example Co")

    def test_supports_graph_and_multiple_job_postings(self):
        html = self.page({"@graph": [
            {"@type": "Organization", "name": "Example Co"},
            {"@type": "JobPosting", "title": "Backend Engineer", "url": "/jobs/backend"},
            {"@type": ["Thing", "JobPosting"], "title": "QA Engineer", "url": "/jobs/qa"},
        ]})
        jobs = extract_job_postings(html, "https://example.org/careers", "Example Co")
        self.assertEqual([job["title"] for job in jobs], ["Backend Engineer", "QA Engineer"])

    def test_ignores_malformed_json_and_non_job_structured_data(self):
        html = (
            '<script type="application/ld+json">{broken</script>'
            + self.page({"@type": "Organization", "name": "Example Co"})
        )
        self.assertEqual(extract_job_postings(html, "https://example.org", "Example Co"), [])

    def test_rejects_missing_titles_and_invalid_urls(self):
        html = self.page({"@graph": [
            {"@type": "JobPosting", "url": "/jobs/no-title"},
            {"@type": "JobPosting", "title": "Engineer", "url": "javascript:alert(1)"},
        ]})
        self.assertEqual(extract_job_postings(html, "https://example.org/careers", "Example Co"), [])

    def test_deduplicates_same_job_url(self):
        html = self.page({"@graph": [
            {"@type": "JobPosting", "title": "Engineer", "url": "/jobs/1"},
            {"@type": "JobPosting", "title": "Engineer duplicate", "url": "/jobs/1"},
        ]})
        jobs = extract_job_postings(html, "https://example.org/careers", "Example Co")
        self.assertEqual(len(jobs), 1)


if __name__ == "__main__":
    unittest.main()
