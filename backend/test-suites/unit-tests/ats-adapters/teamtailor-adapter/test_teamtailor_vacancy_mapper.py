import pytest

from scout.ats_adapters.teamtailor_adapter.teamtailor_vacancy_mapper import (
    map_teamtailor_job,
)


def test_rejects_vacancies_without_a_stable_id_title_or_advert_url() -> None:
    with pytest.raises(ValueError):
        map_teamtailor_job({})


def test_sanitizes_description_and_preserves_exact_advert_url() -> None:
    url = "https://careers.teamviewer.com/jobs/123-role?source=careers"
    vacancy = map_teamtailor_job(
        {
            "guid": "global-id",
            "title": "Engineer",
            "link": url,
            "description": "<script>unsafe()</script><p>Build software</p>",
            "locations": [],
        }
    )
    assert vacancy.application_url == url
    assert vacancy.description == "<p>Build software</p>"
    assert vacancy.published_at is None
    assert vacancy.source_updated_at is None
