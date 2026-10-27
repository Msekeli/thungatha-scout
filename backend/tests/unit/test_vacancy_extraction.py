"""Offline regression tests for deterministic vacancy extraction."""
import unittest

from diagnostics.vacancy_extraction import extract_vacancy_candidate, is_vacancy_detail_url


class VacancyRouteTests(unittest.TestCase):
    def test_accepts_supported_detail_route_families(self):
        cases = [
            ("https://dvtcareers.recruitee.com/o/principal-java-engineer", "Principal Java Engineer"),
            ("https://bbdsoftware.com/jobs/java-engineer-ind26/", "Java Engineer"),
            ("https://culture.entelect.co.za/position/java-team-lead/", "Java Team Lead"),
            ("https://www.stanchionpayments.com/careers/intermediate-java-software-engineer-cape-town/", "Intermediate Java Software Engineer"),
        ]
        for url, title in cases:
            with self.subTest(url=url):
                candidate = extract_vacancy_candidate(
                    {"text": title, "href": url, "card": title + " · Permanent · Cape Town"},
                    "https://example.com/careers", "Example",
                )
                self.assertIsNotNone(candidate)
                self.assertEqual(candidate["title"], title)

    def test_uses_card_context_for_generic_bbd_cta(self):
        candidate = extract_vacancy_candidate(
            {"text": "View Role Details",
             "href": "https://bbdsoftware.com/jobs/java-engineer-ind26/",
             "card": "Java Engineer · Full-time · Cape Town · View Role Details"},
            "https://www.bbd.co.za/careers/", "BBD",
        )
        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["title"], "Java Engineer")
        self.assertEqual(candidate["location"], "Cape Town")
        self.assertTrue(candidate["needs_review"])

    def test_uses_slug_when_ats_link_has_generic_label(self):
        candidate = extract_vacancy_candidate(
            {"text": "Apply", "href": "https://dvtcareers.recruitee.com/o/ai-lead-sdlc-tc-1", "card": ""},
            "https://dvtcareers.recruitee.com/", "DVT",
        )
        self.assertIsNotNone(candidate)
        self.assertIn("Ai Lead", candidate["title"])

    def test_rejects_career_navigation_and_non_job_routes(self):
        for url, label in [
            ("https://www.sovtech.com/careers/library", "Library"),
            ("https://www.sovtech.com/careers/skill-hub", "Skill Hub"),
            ("https://www.sovtech.com/careers/", "Careers"),
            ("https://www.sintrex.com/_files/ugd/123/job.pdf", "VIEW"),
        ]:
            with self.subTest(url=url):
                self.assertFalse(is_vacancy_detail_url(url, "", label))

    def test_keeps_pdf_links_out_of_vacancy_records(self):
        candidate = extract_vacancy_candidate(
            {"text": "VIEW", "href": "https://www.sintrex.com/_files/ugd/job.pdf",
             "card": "Developer Intern · Permanent · Cape Town"},
            "https://www.sintrex.com/careers", "Sintrex",
        )
        self.assertIsNone(candidate)


if __name__ == "__main__":
    unittest.main()
