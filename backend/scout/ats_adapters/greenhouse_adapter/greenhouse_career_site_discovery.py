import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from .greenhouse_career_site_parser import CareersLinks
from scout.employer_name_matching import company_aliases
from .greenhouse_board_resolver import candidate_tokens, resolve_greenhouse_board


async def discover_greenhouse(url: str, company_name: str = "") -> dict[str, str]:
    parsed = urlparse(url.strip())
    if parsed.scheme != "https" or not parsed.hostname:
        raise ValueError("Enter a valid HTTPS careers or jobs URL.")
    if parsed.username or parsed.password:
        raise ValueError("URLs containing credentials are not supported.")
    try:
        addresses = socket.getaddrinfo(parsed.hostname, 443, type=socket.SOCK_STREAM)
    except OSError as exception:
        raise ValueError("Careers page host could not be resolved.") from exception
    if not addresses or any(
        not ipaddress.ip_address(item[4][0]).is_global for item in addresses
    ):
        raise ValueError("Careers page must resolve to a public internet host.")

    async with httpx.AsyncClient(timeout=12, follow_redirects=False) as client:
        response = await client.get(url)
        response.raise_for_status()
        parser = CareersLinks()
        parser.feed(response.text)
        aliases = company_aliases(company_name, parser.title_text, response.url.host)
        candidates = candidate_tokens(parser, response.url, company_name)
        token, board_name = await resolve_greenhouse_board(client, candidates, aliases)

    return {
        "careers_url": str(response.url),
        "board_url": f"https://job-boards.greenhouse.io/{token}",
        "board_token": token,
        "board_name": board_name,
        "detected_adapter": "greenhouse",
        "company_name": board_name,
    }
