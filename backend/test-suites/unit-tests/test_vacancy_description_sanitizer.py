from scout.application.vacancy_description_sanitizer import (
    sanitize_vacancy_description,
)


def test_decodes_entities_and_removes_layout_markup() -> None:
    source = (
        "&lt;div class=&quot;content-intro&quot; style=&quot;color:red&quot;&gt;"
        "&lt;p style=&quot;font-size:12pt&quot;&gt;Build software.&lt;/p&gt;"
        "&lt;/div&gt;"
    )
    assert sanitize_vacancy_description(source) == "<p>Build software.</p>"


def test_preserves_useful_formatting_and_safe_links() -> None:
    source = (
        "<h2>Responsibilities</h2><ul><li><strong>Build</strong></li></ul>"
        '<a href="https://example.com">Apply</a>'
    )
    result = sanitize_vacancy_description(source)
    assert result == (
        "<h2>Responsibilities</h2><ul><li><strong>Build</strong></li></ul>"
        '<a href="https://example.com">Apply</a>'
    )


def test_removes_unsafe_links_and_embedded_active_content() -> None:
    source = (
        '<p>Role</p><a href="javascript:alert(1)">bad link</a>'
        "<script>alert(1)</script><style>p{color:red}</style>"
    )
    assert sanitize_vacancy_description(source) == "<p>Role</p><a>bad link</a>"


def test_plain_text_remains_readable() -> None:
    assert sanitize_vacancy_description("Build reliable software.") == (
        "Build reliable software."
    )
