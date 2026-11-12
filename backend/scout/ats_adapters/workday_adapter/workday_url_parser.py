import re
from urllib.parse import urlsplit


def parse_workday_board_url(source_url: str) -> tuple[dict[str, str], str]:
    parsed = urlsplit(source_url.strip())
    host = parsed.hostname or ""
    labels = host.split(".")
    if parsed.scheme != "https" or parsed.netloc.lower() != host:
        raise ValueError("Use a standard HTTPS Workday careers URL.")
    if len(labels) != 4:
        raise ValueError("URL is not hosted by myworkdayjobs.com.")
    tenant, cluster, domain, suffix = labels
    if domain != "myworkdayjobs" or suffix != "com":
        raise ValueError("URL is not hosted by myworkdayjobs.com.")
    if not re.fullmatch(r"[a-z0-9-]+", tenant):
        raise ValueError("Workday tenant in the host is invalid.")
    if not re.fullmatch(r"wd[0-9]+", cluster):
        raise ValueError("Workday host cluster is invalid.")
    parts = [part for part in parsed.path.split("/") if part]
    locale = "en-US"
    if parts and re.fullmatch(r"[a-z]{2}-[A-Z]{2}", parts[0]):
        locale = parts.pop(0)
    if len(parts) != 1 or not re.fullmatch(r"[A-Za-z0-9_-]+", parts[0]):
        raise ValueError("Use a Workday board URL, not an individual job URL.")
    site = parts[0]
    config = {"host_prefix": f"{tenant}.{cluster}", "tenant": tenant, "site": site, "locale": locale}
    return config, f"https://{host}/{locale}/{site}"
