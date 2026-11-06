import json
from functools import lru_cache
from pathlib import Path

_TERMS_PATH = (
    Path(__file__).resolve().parents[2]
    / "registry"
    / "vacancy-location-scopes.json"
)


@lru_cache(maxsize=1)
def _location_terms() -> dict[str, tuple[str, ...]]:
    data = json.loads(_TERMS_PATH.read_text(encoding="utf-8"))
    return {scope: tuple(terms) for scope, terms in data.items()}


def location_scope_condition(scope: str) -> tuple[str, list[str]]:
    if scope in {"all", "south_africa"}:
        return "", []
    terms = _location_terms().get(scope)
    if terms is None:
        raise ValueError("Unsupported vacancy location scope.")
    normalized = (
        "regexp_replace(lower(coalesce(v.location_text, '')), "
        "'[^a-z0-9]+', ' ', 'g')"
    )
    conditions = [f"{normalized} ~ %s" for _ in terms]
    parameters = [rf"(^| ){term}( |$)" for term in terms]
    return "(" + " OR ".join(conditions) + ")", parameters
