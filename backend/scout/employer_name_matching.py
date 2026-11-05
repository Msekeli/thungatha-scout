import re
from collections.abc import Sequence

_SUFFIXES = {
    "group",
    "holdings",
    "inc",
    "limited",
    "ltd",
    "plc",
    "company",
    "sa",
    "labs",
    "technologies",
    "technology",
    "systems",
    "solutions",
    "global",
}
_SUBDOMAINS = {"www", "careers", "jobs", "job", "apply", "work"}
_MULTI_PART_SUFFIXES = {"co.za", "co.uk", "com.au", "co.nz", "com.br", "co.in"}


def normalise_company_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def domain_company_name(hostname: str) -> str:
    labels = [part for part in hostname.split(".") if part and part not in _SUBDOMAINS]
    suffix = ".".join(labels[-2:])
    if suffix in _MULTI_PART_SUFFIXES and len(labels) >= 3:
        return labels[-3]
    return labels[-2] if len(labels) > 1 else labels[0] if labels else ""


def company_aliases(name: str, title: str, hostname: str) -> list[str]:
    values = [name, title.split("|")[0].split("—")[0], domain_company_name(hostname)]
    return list(dict.fromkeys(normalise_company_name(v) for v in values if v.strip()))


def board_name_matches(board_name: str, aliases: Sequence[str]) -> bool:
    actual = normalise_company_name(board_name)
    return any(
        actual == alias
        or actual.startswith(alias)
        and actual[len(alias) :] in _SUFFIXES
        for alias in aliases
    )
