from collections import deque
from urllib.parse import urlsplit

import httpx

from scout.ats_adapters.greenhouse_adapter.greenhouse_career_site_discovery import (
    discover_greenhouse,
)
from scout.ats_adapters.greenhouse_adapter.greenhouse_contracts import parse_board_token
from scout.ats_adapters.lever_adapter.lever_url_parser import parse_lever_board_url
from scout.application.careers_page_reader import read_careers_page

LEVER_HOSTS = {"jobs.lever.co", "jobs.eu.lever.co"}
GREENHOUSE_HOSTS = {
    "boards.greenhouse.io",
    "job-boards.greenhouse.io",
    "job-boards.eu.greenhouse.io",
}


async def _inspect_lever(url: str, company_name: str) -> dict:
    from scout.api.lever_routes import inspect_lever_board

    return await inspect_lever_board(url, company_name)


async def _inspect_greenhouse(url: str, company_name: str) -> dict:
    result = await discover_greenhouse(url, company_name)
    result.update({"outcome": "success", "complete": True, "jobs": []})
    return result


async def _discover_from_page(url: str, company_name: str) -> dict:
    origin = urlsplit(url)
    queue = deque([(url, 0)])
    visited: set[str] = set()
    candidates: dict[tuple[str, str], str] = {}
    async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
        while queue and len(visited) < 12:
            page_url, depth = queue.popleft()
            if page_url in visited:
                continue
            visited.add(page_url)
            final_url, links = await read_careers_page(client, page_url)
            for href in links:
                target = httpx.URL(final_url).join(href)
                host = target.host
                if host in LEVER_HOSTS:
                    _, board_url = parse_lever_board_url(str(target))
                    candidates[("lever", board_url)] = str(target)
                elif host in GREENHOUSE_HOSTS:
                    token = parse_board_token(str(target))
                    candidates[("greenhouse", token)] = str(target)
                elif (
                    depth < 2
                    and target.scheme == "https"
                    and target.host == origin.hostname
                ):
                    queue.append((str(target), depth + 1))
    if len(candidates) != 1:
        raise ValueError(
            "Could not identify one unambiguous ATS board from this careers page. "
            "Paste the employer's direct ATS board URL."
        )
    (adapter, _), board_link = next(iter(candidates.items()))
    if adapter == "lever":
        return await _inspect_lever(board_link, company_name)
    return await _inspect_greenhouse(board_link, company_name)


async def discover_careers_source(url: str, company_name: str = "") -> dict:
    host = urlsplit(url).hostname or ""
    if host in LEVER_HOSTS:
        result = await _inspect_lever(url, company_name)
    elif host in GREENHOUSE_HOSTS:
        result = await _inspect_greenhouse(url, company_name)
    else:
        result = await _discover_from_page(url, company_name)
    result["careers_url"] = url
    result["company_name"] = company_name or result.get("company_name", "")
    return result
