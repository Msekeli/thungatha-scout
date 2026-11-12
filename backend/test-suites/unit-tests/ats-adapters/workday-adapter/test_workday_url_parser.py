import pytest

from scout.ats_adapters.workday_adapter.workday_config import workday_cxs_base_url
from scout.ats_adapters.workday_adapter.workday_url_parser import (
    parse_workday_board_url,
)


def test_parses_locale_and_host_components_independently() -> None:
    config, url = parse_workday_board_url(
        "https://myhcm.wd3.myworkdayjobs.com/fr-FR/digioutsource"
    )
    assert config == {
        "host_prefix": "myhcm.wd3",
        "tenant": "myhcm",
        "site": "digioutsource",
        "locale": "fr-FR",
    }
    assert url == "https://myhcm.wd3.myworkdayjobs.com/fr-FR/digioutsource"


def test_defaults_locale_when_board_url_has_no_locale() -> None:
    config, _ = parse_workday_board_url(
        "https://oldmutual.wd3.myworkdayjobs.com/Old_Mutual_Careers"
    )
    assert config["tenant"] == "oldmutual"
    assert config["site"] == "Old_Mutual_Careers"
    assert config["locale"] == "en-US"


def test_rejects_invalid_optional_locale_in_saved_config() -> None:
    with pytest.raises(ValueError, match="locale"):
        workday_cxs_base_url({
            "host_prefix": "myhcm.wd3",
            "tenant": "myhcm",
            "site": "digioutsource",
            "locale": "../invalid",
        })


@pytest.mark.parametrize("url", [
    "http://myhcm.wd3.myworkdayjobs.com/digioutsource",
    "https://example.com/digioutsource",
    "https://myhcm.wd3.myworkdayjobs.com/job/Cape-Town/Role",
    "https://myhcm.wd3.myworkdayjobs.com/en-US",
    "https://user@myhcm.wd3.myworkdayjobs.com/digioutsource",
    "https://myhcm.wd3.myworkdayjobs.com:8443/digioutsource",
])
def test_rejects_non_board_urls(url: str) -> None:
    with pytest.raises(ValueError):
        parse_workday_board_url(url)
