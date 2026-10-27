"""Offline tests for careers investigation candidate validation."""
import unittest

from diagnostics.investigate_careers import (
    _extract_visible_jobs,
    _has_vacancy_card_evidence,
    validate_job_list,
)


class NetworkJobValidationTests(unittest.TestCase):
    def test_accepts_a_list_of_job_records(self):
        records = [
            {"title": "Backend Engineer", "id": "123", "location": "Cape Town"},
            {"title": "Product Designer", "id": "124", "department": "Product"},
            {"title": "QA Engineer", "url": "/jobs/qa", "employmentType": "Full-time"},
        ]
        jobs = validate_job_list(records)
        self.assertEqual(len(jobs), 3)
        self.assertEqual(jobs[0]["title"], "Backend Engineer")

    def test_rejects_navigation_links(self):
        records = [
            {"title": "Home", "url": "/"},
            {"title": "Careers", "url": "/careers"},
            {"title": "Login", "url": "/login"},
        ]
        self.assertEqual(validate_job_list(records), [])

    def test_rejects_records_without_job_signals(self):
        records = [
            {"title": "Backend Engineer", "id": "1"},
            {"title": "Product Designer", "id": "2"},
            {"title": "QA Engineer", "id": "3"},
        ]
        self.assertEqual(validate_job_list(records), [])

    def test_finds_nested_job_list(self):
        payload = {"data": {"results": [
            {"title": "Backend Engineer", "id": "1", "location": "Cape Town"},
            {"title": "Product Designer", "id": "2", "department": "Design"},
        ]}}
        self.assertEqual(len(validate_job_list(payload)), 2)

    def test_accepts_a_single_record_with_location_evidence(self):
        jobs = validate_job_list([
            {"title": "Backend Engineer", "id": "1", "location": "Cape Town"}
        ])
        self.assertEqual(len(jobs), 1)
        self.assertEqual(jobs[0]["location"], "Cape Town")


class VacancyCardEvidenceTests(unittest.TestCase):
    def test_rejects_career_page_content_without_vacancy_signals(self):
        self.assertFalse(_has_vacancy_card_evidence("Library Skill Hub Learn more"))

    def test_accepts_card_with_location_and_employment_type(self):
        self.assertTrue(
            _has_vacancy_card_evidence(
                "Software Engineer · Full-time · Cape Town · View role"
            )
        )

    def test_accepts_card_with_closing_date(self):
        self.assertTrue(
            _has_vacancy_card_evidence(
                "Software Engineer Closes 30 Nov 2026 View role"
            )
        )


class VisibleHtmlExtractionTests(unittest.TestCase):
    def test_extracts_vacancy_from_listing_link_and_context(self):
        class FakePage:
            def evaluate(self, _script):
                return [{
                    "text": "View role",
                    "href": "https://example.com/careers/software-engineer-junior",
                    "card": "Software Engineer (Junior) Software Engineering · Stellenbosch, South Africa (Hybrid) Closes 30 Nov 2026 View role",
                }]

        jobs = _extract_visible_jobs(
            FakePage(), "https://example.com/careers", "Example"
        )
        self.assertEqual(len(jobs), 1)
        self.assertIn("Software Engineer", jobs[0]["title"])
        self.assertIn("Stellenbosch", jobs[0]["location"])
        self.assertEqual(jobs[0]["closing_date_text"], "30 Nov 2026")
        self.assertTrue(jobs[0]["needs_review"])


if __name__ == "__main__":
    unittest.main()
