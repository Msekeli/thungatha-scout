from types import SimpleNamespace

from scout.crawling.career_page_observer import observe_page


def _context(url: str, body: bytes, status: int = 200):
    return SimpleNamespace(
        request=SimpleNamespace(url=url, loaded_url=url),
        http_response=SimpleNamespace(
            status_code=status,
            headers={"content-type": "text/html; charset=utf-8"},
        ),
    ), body


def test_only_https_career_links_and_known_ats_links_are_discovered() -> None:
    context, body = _context(
        "https://employer.example/careers",
        b'<a href="/jobs">Jobs</a>'
        b'<a href="http://employer.example/openings">HTTP</a>'
        b'<a href="https://other.example/careers">Other</a>'
        b'<a href="https://boards.greenhouse.io/acme/jobs">'
        b"Careers</a>"
        b'<a href="https://boards.greenhouse.io/acme">Home</a>',
    )
    result = observe_page(context, body, False)
    assert result.discovered_links == (
        "https://employer.example/jobs",
        "https://boards.greenhouse.io/acme/jobs",
    )


def test_blocked_and_transient_responses_are_classified() -> None:
    blocked, body = _context("https://employer.example/careers", b"", 403)
    transient, _ = _context("https://employer.example/careers", b"", 503)
    assert observe_page(blocked, body, False).outcome == "blocked"
    assert observe_page(transient, body, False).outcome == "transient_failure"


def test_oversized_response_is_not_parsed() -> None:
    context, body = _context(
        "https://employer.example/careers",
        b'<script type="application/ld+json">{"@type":"JobPosting"}</script>',
    )
    result = observe_page(context, body, True)
    assert result.outcome == "response_too_large"
    assert result.vacancies == ()


def test_discovered_links_are_bounded_per_page() -> None:
    anchors = "".join(
        f'<a href="/careers/{index}">Career {index}</a>' for index in range(30)
    )
    context, body = _context(
        "https://employer.example/careers",
        anchors.encode(),
    )
    assert len(observe_page(context, body, False).discovered_links) == 20
