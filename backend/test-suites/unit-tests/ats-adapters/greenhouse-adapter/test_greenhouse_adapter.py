import pytest

from scout.ats_adapters.greenhouse_adapter.greenhouse_contracts import GreenhouseUrlError, parse_board_token


def test_parse_supported_greenhouse_board_urls() -> None:
    assert (
        parse_board_token("https://job-boards.greenhouse.io/takealotgroup")
        == "takealotgroup"
    )
    assert (
        parse_board_token(
            "https://job-boards.eu.greenhouse.io/bashdotcom/jobs/5017437101"
        )
        == "bashdotcom"
    )
    assert (
        parse_board_token("https://boards.greenhouse.io/embed/job_board?for=example")
        == "example"
    )


@pytest.mark.parametrize(
    "url",
    [
        "http://boards.greenhouse.io/example",
        "https://boards.greenhouse.io.evil.test/example",
        "https://example.com/careers",
        "https://job-boards.greenhouse.io/",
        "https://user@job-boards.eu.greenhouse.io/example",
    ],
)
def test_reject_unsupported_board_urls(url: str) -> None:
    with pytest.raises(GreenhouseUrlError):
        parse_board_token(url)
