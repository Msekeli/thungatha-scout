import ipaddress
import socket
from urllib.parse import urlparse

import httpx

from scout.career_site_html_parser import (
    CareersLinks,
    find_greenhouse_board_reference,
)


async def discover_greenhouse(url: str) -> dict[str, str]:
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
    reference = find_greenhouse_board_reference(parser, response.url)
    if reference:
        token, board_url = reference
        return {
            "careers_url": str(response.url),
            "board_url": board_url,
            "board_token": token,
            "detected_adapter": "greenhouse",
            "company_name": parser.title_text.split("|")[0].split("—")[0].strip(),
        }
    raise ValueError(
        "No Greenhouse board reference was found in links or embedded scripts."
    )
