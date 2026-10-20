from app.site_investigator import _detect_ats, _greenhouse_board, _workday_config


def test_detect_workday_from_host_and_page_config():
    html = 'window.workday = window.workday || { tenant: "relx", siteId: "relx" };'
    ats = _detect_ats(html, "https://relx.wd3.myworkdayjobs.com/relx", [])
    assert "workday" in ats
    assert _workday_config(html, "https://relx.wd3.myworkdayjobs.com/relx") == {
        "host": "relx.wd3.myworkdayjobs.com",
        "tenant": "relx",
        "site": "relx",
        "status": "identified",
    }


def test_greenhouse_board_token_requires_page_evidence():
    html = 'fetch("https://boards-api.greenhouse.io/v1/boards/ozow/jobs?content=true")'
    assert _greenhouse_board(html, "https://ozow.com/jobs") == "ozow"


def test_workday_incomplete_config_is_not_marked_identified():
    config = _workday_config("", "https://relx.wd3.myworkdayjobs.com/relx")
    assert config is not None
    assert config["status"] == "incomplete_config"


def test_ordinary_site_does_not_get_an_ats_guess():
    assert _detect_ats("<html><title>Careers</title></html>", "https://example.com/careers", []) == []
    assert _greenhouse_board("<html></html>", "https://example.com/careers") is None
