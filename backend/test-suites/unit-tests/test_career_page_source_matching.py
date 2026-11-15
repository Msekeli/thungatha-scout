from types import SimpleNamespace

from scout.application.career_page_source_matching import match_existing_source


def test_matches_detected_ats_to_existing_registered_source() -> None:
    sources = [
        {
            "adapter_key": "greenhouse",
            "source_url": "https://boards.greenhouse.io/acme",
        }
    ]
    pages = (
        SimpleNamespace(
            final_url="https://boards.greenhouse.io/acme/jobs/123",
            platform_key="greenhouse",
        ),
    )
    assert match_existing_source(sources, pages) == sources[0]


def test_does_not_match_another_board_on_the_same_ats_host() -> None:
    sources = [
        {
            "adapter_key": "greenhouse",
            "source_url": "https://boards.greenhouse.io/other-company",
        }
    ]
    pages = (
        SimpleNamespace(
            final_url="https://boards.greenhouse.io/acme",
            platform_key="greenhouse",
        ),
    )
    assert match_existing_source(sources, pages) is None


def test_custom_domain_source_matches_its_exact_registered_url() -> None:
    sources = [
        {
            "adapter_key": "teamtailor",
            "source_url": "https://careers.example.com/jobs",
        }
    ]
    pages = (
        SimpleNamespace(
            final_url="https://careers.example.com/jobs",
            platform_key=None,
        ),
    )
    assert match_existing_source(sources, pages) == sources[0]


def test_career_page_source_is_not_its_own_ats_target() -> None:
    sources = [
        {
            "adapter_key": "career_page",
            "source_url": "https://example.com/careers",
        }
    ]
    pages = (
        SimpleNamespace(
            final_url="https://example.com/careers",
            platform_key=None,
        ),
    )
    assert match_existing_source(sources, pages) is None
