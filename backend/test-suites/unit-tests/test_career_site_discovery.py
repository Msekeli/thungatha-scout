from scout.career_site_discovery import CareersLinks


def test_careers_page_parser_collects_title_and_ats_links() -> None:
    parser = CareersLinks()
    parser.feed(
        "<html><title>Ozow Careers</title>"
        '<a href="https://job-boards.greenhouse.io/ozow/jobs/123">Role</a>'
        "</html>"
    )

    assert parser.title_text == "Ozow Careers"
    assert parser.links == ["https://job-boards.greenhouse.io/ozow/jobs/123"]
