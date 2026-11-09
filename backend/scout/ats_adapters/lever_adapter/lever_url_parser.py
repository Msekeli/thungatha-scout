from urllib.parse import urlsplit
import re


LEVER_BOARD_HOSTS = {"jobs.lever.co": "global", "jobs.eu.lever.co": "eu"}


def parse_lever_board_url(source_url: str) -> tuple[dict[str, str], str]:
    parsed = urlsplit(source_url)
    region = LEVER_BOARD_HOSTS.get(parsed.hostname or "")
    if (
        parsed.scheme != "https"
        or region is None
        or parsed.port is not None
        or parsed.username is not None
        or parsed.password is not None
    ):
        raise ValueError("Use an HTTPS jobs.lever.co or jobs.eu.lever.co board URL.")
    segments = [segment for segment in parsed.path.split("/") if segment]
    if not segments or len(segments) > 2:
        raise ValueError("Lever URL must identify a board or a posting on that board.")
    slug = segments[0]
    if not re.fullmatch(r"[A-Za-z0-9_-]+", slug):
        raise ValueError("Lever board URL contains an invalid site identifier.")
    config = {"slug": slug, "region": region}
    board_url = f"https://{parsed.hostname}/{slug}"
    return config, board_url
