import pytest

from scout.ats_adapters.workable_adapter.workable_url_parser import (
    parse_workable_board_url,
)


def test_parses_workable_board_url() -> None:
    config, board_url = parse_workable_board_url(
        "https://apply.workable.com/lekkeslaap/"
    )

    assert config == {"slug": "lekkeslaap"}
    assert board_url == "https://apply.workable.com/lekkeslaap"


@pytest.mark.parametrize(
    "url",
    [
        "http://apply.workable.com/example/",
        "https://example.com/careers",
        "https://apply.workable.com/example/jobs/123",
        "https://apply.workable.com/",
    ],
)
def test_rejects_unsupported_workable_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_workable_board_url(url)
