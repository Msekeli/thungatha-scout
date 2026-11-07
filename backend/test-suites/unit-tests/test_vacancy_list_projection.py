from scout.persistence.vacancy_repository import VacancyRepository
from dashboard_bulk_read_test_connection import FakeConnection


def test_active_vacancy_list_omits_full_description_payload() -> None:
    connection = FakeConnection([])
    VacancyRepository(connection).list_all()

    query = connection.queries[0][0]
    assert "v.title" in query
    assert "e.logo_url AS employer_logo_url" in query
    assert "e.logo_source_url AS employer_logo_source_url" in query
    assert "v.*" not in query
    assert "v.description" not in query
    assert "raw_payload" not in query


def test_vacancy_detail_query_still_returns_full_record() -> None:
    connection = FakeConnection([{"description": "<p>Full details</p>"}])
    result = VacancyRepository(connection).get_by_id("vacancy-id")

    assert result["description"] == "<p>Full details</p>"
    assert "SELECT v.*" in connection.queries[0][0]


def test_cape_town_page_applies_location_scope_and_pagination() -> None:
    connection = FakeConnection([{"total": 31}])
    result = VacancyRepository(connection).list_page(
        location_scope="cape_town", limit=10, offset=20
    )

    assert result["total"] == 31
    assert result["has_more"] is True
    assert "regexp_replace" in connection.queries[0][0]
    assert len(connection.queries[0][1]) == 30
    assert connection.queries[1][1][-2:] == [10, 20]


def test_employer_vacancy_list_keeps_employer_filter() -> None:
    connection = FakeConnection([])
    VacancyRepository(connection).list_for_employer("employer-id", 12, 3)

    query, parameters = connection.queries[0]
    assert "v.employer_id = %s" in query
    assert parameters == ["employer-id", 12, 3]


def test_export_query_returns_the_public_scout_projection() -> None:
    connection = FakeConnection([{"total": 3}])
    result = VacancyRepository(connection).export_page(limit=25, offset=0)

    export_query, parameters = connection.queries[1]
    assert result["total"] == 3
    assert result["location_scope"] == "south_africa"
    assert "v.status = 'active'" in export_query
    assert "v.archived_at IS NULL" in export_query
    assert "v.id AS scout_vacancy_id" in export_query
    assert "e.name AS employer_name" in export_query
    assert "e.logo_url" in export_query
    assert "v.description" in export_query
    assert "v.published_at" in export_query
    assert "v.source_updated_at" in export_query
    assert "v.first_seen_at" in export_query
    assert "raw_payload" not in export_query
    assert "external_job_id" not in export_query
    assert "source_url" not in export_query
    assert "ORDER BY v.published_at DESC NULLS LAST" in export_query
    assert "v.id ASC" in export_query
    assert parameters == (25, 0)
