import pytest

from scout.persistence.vacancy_location_scope import location_scope_condition


def test_cape_town_scope_builds_location_predicates() -> None:
    condition, parameters = location_scope_condition("cape_town")
    assert "regexp_replace" in condition
    assert len(parameters) == 28
    assert r"(^| )cape town( |$)" in parameters
    assert r"(^| )ct( |$)" not in parameters
    assert r"(^| )cpt( |$)" not in parameters


def test_western_cape_scope_includes_regional_terms() -> None:
    _, parameters = location_scope_condition("western_cape")
    assert r"(^| )western cape( |$)" in parameters
    assert r"(^| )stellenbosch( |$)" in parameters
    assert r"(^| )paarl( |$)" in parameters


@pytest.mark.parametrize("scope", ["all", "south_africa"])
def test_broad_scopes_do_not_add_location_predicates(scope: str) -> None:
    assert location_scope_condition(scope) == ("", [])


def test_unknown_scope_is_rejected() -> None:
    with pytest.raises(ValueError, match="Unsupported vacancy location scope"):
        location_scope_condition("unknown")
