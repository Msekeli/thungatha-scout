from scout.persistence.vacancy_repository import VacancyRepository
from dashboard_bulk_read_test_connection import FakeConnection


def test_active_vacancy_list_omits_full_description_payload() -> None:
    connection = FakeConnection([])
    VacancyRepository(connection).list_all()

    query = connection.queries[0][0]
    assert "v.title" in query
    assert "v.*" not in query
    assert "v.description" not in query
    assert "raw_payload" not in query


def test_vacancy_detail_query_still_returns_full_record() -> None:
    connection = FakeConnection([{"description": "<p>Full details</p>"}])
    result = VacancyRepository(connection).get_by_id("vacancy-id")

    assert result["description"] == "<p>Full details</p>"
    assert "SELECT v.*" in connection.queries[0][0]
