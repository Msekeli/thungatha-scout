"""Offline tests for careers investigation candidate validation."""
import unittest

from diagnostics.investigate_careers import validate_job_list


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


if __name__ == "__main__":
    unittest.main()
