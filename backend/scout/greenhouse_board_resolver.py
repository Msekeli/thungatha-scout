import re
from collections.abc import Sequence

import httpx

from scout.career_site_html_parser import CareersLinks, find_greenhouse_board_candidates

API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
_SUFFIXES = {"group", "holdings", "inc", "limited", "ltd", "plc", "company", "sa"}


def normalise_company_name(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def company_aliases(name: str, title: str, hostname: str) -> list[str]:
    labels = [part for part in hostname.split(".") if part]
    labels = [part for part in labels if part not in {"www", "careers", "jobs", "job"}]
    domain_name = labels[-3] if len(labels) >= 3 and labels[-2:] == ["co", "za"] else labels[-2] if len(labels) > 1 else labels[0] if labels else ""
    values = [name, title.split("|")[0].split("—")[0], domain_name]
    return list(dict.fromkeys(normalise_company_name(value) for value in values if value.strip()))


def board_name_matches(board_name: str, aliases: Sequence[str]) -> bool:
    actual = normalise_company_name(board_name)
    for alias in aliases:
        if actual == alias:
            return True
        if actual.startswith(alias) and actual[len(alias):] in _SUFFIXES:
            return True
    return False


def candidate_tokens(
    parser: CareersLinks, page_url: httpx.URL, company_name: str
) -> list[str]:
    candidates = find_greenhouse_board_candidates(parser, page_url)
    for value in (company_name, page_url.host.split(".")[0]):
        token = re.sub(r"[^a-z0-9-]", "", value.casefold().replace(" ", "-"))
        if token and token not in candidates:
            candidates.append(token)
    return candidates


async def resolve_greenhouse_board(
    client: httpx.AsyncClient,
    candidates: Sequence[str],
    aliases: Sequence[str],
) -> tuple[str, str]:
    for token in candidates:
        response = await client.get(f"{API_ROOT}/{token}")
        if response.status_code == 404:
            continue
        response.raise_for_status()
        try:
            payload = response.json()
            board_name = payload.get("name") if isinstance(payload, dict) else None
        except ValueError:
            continue
        if isinstance(board_name, str) and board_name_matches(board_name, aliases):
            return token, board_name
    raise ValueError(
        "Greenhouse was detected, but its board could not be confirmed for this company. "
        "Check the careers URL or provide a Greenhouse board URL."
    )
