import asyncio
import re
from collections.abc import Sequence

import httpx

from .greenhouse_career_site_parser import CareersLinks, find_greenhouse_board_candidates
from scout.employer_name_matching import board_name_matches, domain_company_name

API_ROOT = "https://boards-api.greenhouse.io/v1/boards"


def candidate_tokens(
    parser: CareersLinks, page_url: httpx.URL, company_name: str
) -> list[str]:
    candidates = find_greenhouse_board_candidates(parser, page_url)
    for value in (company_name, domain_company_name(page_url.host)):
        token = re.sub(r"[^a-z0-9-]", "", value.casefold().replace(" ", "-"))
        if token and token not in candidates:
            candidates.append(token)
    return candidates


async def _check_candidate(
    client: httpx.AsyncClient, token: str, aliases: Sequence[str]
) -> tuple[str, str] | None:
    response = await client.get(f"{API_ROOT}/{token}")
    if response.status_code == 404:
        return None
    response.raise_for_status()
    try:
        payload = response.json()
    except ValueError:
        return None
    board_name = payload.get("name") if isinstance(payload, dict) else None
    if isinstance(board_name, str) and board_name_matches(board_name, aliases):
        return token, board_name
    return None


async def resolve_greenhouse_board(
    client: httpx.AsyncClient,
    candidates: Sequence[str],
    aliases: Sequence[str],
) -> tuple[str, str]:
    results = await asyncio.gather(
        *(_check_candidate(client, token, aliases) for token in candidates),
        return_exceptions=True,
    )
    for result in results:
        if isinstance(result, tuple):
            return result
    for result in results:
        if isinstance(result, Exception):
            raise result
    raise ValueError(
        "Greenhouse was detected, but its board could not be confirmed for this company. "
        "Check the careers URL or provide a Greenhouse board URL."
    )
