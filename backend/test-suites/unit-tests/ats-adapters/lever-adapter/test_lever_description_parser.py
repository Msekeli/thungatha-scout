from scout.ats_adapters.lever_adapter.lever_description_parser import (
    extract_lever_description,
)


def test_prefers_non_empty_plain_description() -> None:
    assert extract_lever_description(" Plain text ", "<p>HTML</p>") == "Plain text"


def test_extracts_html_paragraphs_and_entities() -> None:
    html = "<div><p>First&nbsp;paragraph</p><p><strong>Second</strong></p></div>"
    assert extract_lever_description(None, html) == "First paragraph\nSecond"


def test_returns_none_when_both_descriptions_are_empty() -> None:
    assert extract_lever_description("", "  ") is None
