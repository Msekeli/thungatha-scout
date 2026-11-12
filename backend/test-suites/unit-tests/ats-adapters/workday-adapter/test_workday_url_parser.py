import pytest

from scout.ats_adapters.workday_adapter.workday_url_parser import (
    parse_workday_board_url,
)


def test_parses_locale_and_host_components_independently() -> None:
    config, url = parse_workday_board_url(
        "https://myhcm.wd3.myworkdayjobs.com/en-US/digioutsource"
    )
    assert config == {
        "host_prefix": "myhcm.wd3",
        "tenant": "myhcm",
        "site": "digioutsource",
    }
    assert url == "https://myhcm.wd3.myworkdayjobs.com/en-US/digioutsource"


def test_parses_board_without_locale() -> None:
    config, _ = parse_workday_board_url(
        "https://oldmutual.wd3.myworkdayjobs.com/Old_Mutual_Careers"
    )
    assert config["tenant"] == "oldmutual"
    assert config["site"] == "Old_Mutual_Careers"


@pytest.mark.parametrize(
    "url",
    [
        "http://myhcm.wd3.myworkdayjobs.com/digioutsource",
        "https://example.com/digioutsource",
        "https://myhcm.wd3.myworkdayjobs.com/job/Cape-Town/Role",
        "https://myhcm.wd3.myworkdayjobs.com/en-US",
    ],
)
def test_rejects_non_board_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_workday_board_url(url)
