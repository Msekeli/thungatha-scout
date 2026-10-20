from app.verification import CAREER_KEYWORDS


def test_careers_keywords_include_common_variants():
    assert "careers" in CAREER_KEYWORDS
    assert "vacancies" in CAREER_KEYWORDS
    assert "jobs" in CAREER_KEYWORDS
