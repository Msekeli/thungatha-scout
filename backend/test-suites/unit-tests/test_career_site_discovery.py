from httpx import URL

from scout.career_site_html_parser import CareersLinks, find_greenhouse_board_reference


def test_careers_page_parser_collects_title_and_ats_links() -> None:
    parser = CareersLinks()
    parser.feed(
        "<html><title>Ozow Careers</title>"
        '<a href="https://job-boards.greenhouse.io/ozow/jobs/123">Role</a>'
        "</html>"
    )

    assert parser.title_text == "Ozow Careers"
    assert parser.links == ["https://job-boards.greenhouse.io/ozow/jobs/123"]


def test_board_reference_uses_greenhouse_job_board_links() -> None:
    parser = CareersLinks()
    parser.feed('<a href="https://job-boards.greenhouse.io/ozow/jobs/123">Role</a>')

    assert find_greenhouse_board_reference(parser, URL("https://ozow.com/jobs")) == (
        "ozow",
        "https://job-boards.greenhouse.io/ozow",
    )


def test_board_reference_detects_inline_greenhouse_api_configuration() -> None:
    parser = CareersLinks()
    parser.feed(
        "<html><title>Ozow Careers | Come Aboard</title>"
        "<script>fetch('https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true')</script>"
        "</html>"
    )

    assert find_greenhouse_board_reference(parser, URL("https://ozow.com/jobs")) == (
        "ozow",
        "https://job-boards.greenhouse.io/ozow",
    )
