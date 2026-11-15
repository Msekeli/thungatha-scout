import re
from typing import Any

_OFFICE_SUFFIX = re.compile(
    r"\s+(?:dc|office|hub|distribution centre|distribution center|"
    r"cross dock facility|facility|warehouse)$",
    re.IGNORECASE,
)
_BROAD_LOCATIONS = {
    "south africa",
    "western cape",
    "eastern cape",
    "northern cape",
    "gauteng",
    "kwazulu natal",
    "kwa zulu natal",
    "free state",
    "north west",
    "limpopo",
    "mpumalanga",
}
_GENERIC_OFFICES = {"head", "main", "regional", "national"}


def _office_location_names(offices: Any) -> list[str]:
    if not isinstance(offices, list):
        return []
    names: list[str] = []
    for office in offices:
        if not isinstance(office, dict) or not isinstance(office.get("name"), str):
            continue
        name = office["name"].strip()
        canonical = _OFFICE_SUFFIX.sub("", name).strip(" ,-/")
        if canonical and canonical.casefold() not in _GENERIC_OFFICES:
            if canonical.casefold() not in {item.casefold() for item in names}:
                names.append(canonical)
    return names


def resolve_greenhouse_location(location: Any, offices: Any) -> str | None:
    location_name = (
        location.get("name").strip()
        if isinstance(location, dict) and isinstance(location.get("name"), str)
        else location.strip()
        if isinstance(location, str)
        else ""
    )
    office_names = _office_location_names(offices)
    if office_names and (
        not location_name or location_name.casefold() in _BROAD_LOCATIONS
    ):
        return " | ".join(office_names)
    if location_name:
        return location_name
    return " | ".join(office_names) if office_names else None
