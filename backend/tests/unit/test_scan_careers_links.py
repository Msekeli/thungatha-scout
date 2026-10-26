"""Regression tests for conservative career-page link classification."""
import unittest

from scan_careers import _is_job_link

SOURCE = "https://careers.sanlamcloud.co.za/"


class JobLinkClassificationTests(unittest.TestCase):
    def test_rejects_informational_sanlam_links(self):
        examples = [
            ("Working at Sanlam", "https://careers.sanlamcloud.co.za/content/Working-at-Sanlam/?locale=en_GB"),
            ("How we recruit", "https://careers.sanlamcloud.co.za/content/How-we-recruit/?locale=en_GB"),
            ("Join Talent Community", "https://career5.successfactors.eu/career?career_company=sanlamlifeP2"),
            ("Screen readers cannot read the following searchable map.", "https://careers.sanlamcloud.co.za/search"),
        ]
        for text, href in examples:
            with self.subTest(text=text):
                self.assertFalse(_is_job_link({"text": text, "href": href}, SOURCE))

    def test_does_not_score_careers_hostname_as_job_evidence(self):
        self.assertFalse(_is_job_link({
            "text": "About us",
            "href": "https://careers.example.com/about",
            "card_text": "",
        }, "https://careers.example.com/"))

    def test_accepts_job_specific_path(self):
        self.assertTrue(_is_job_link({
            "text": "Software Engineer",
            "href": "https://careers.example.com/jobs/software-engineer-123",
            "card_text": "Software Engineer Cape Town Permanent",
        }, "https://careers.example.com/"))

    def test_accepts_job_title_in_employment_card_with_action(self):
        self.assertTrue(_is_job_link({
            "text": "Apply now",
            "href": "https://example.com/role/123",
            "card_text": "Software Engineer Cape Town Full-time Apply now",
        }, "https://example.com/careers"))


if __name__ == "__main__":
    unittest.main()
