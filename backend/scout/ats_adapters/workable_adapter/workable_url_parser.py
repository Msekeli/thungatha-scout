from urllib.parse import urlsplit


def parse_workable_board_url(source_url: str) -> tuple[dict[str, str], str]:
    parsed = urlsplit(source_url.strip())
    if parsed.scheme != "https" or parsed.hostname != "apply.workable.com":
        raise ValueError("Use an HTTPS Workable careers board URL.")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 1 or not parts[0].replace("-", "").replace("_", "").isalnum():
        raise ValueError("Use a Workable company board URL, not an individual job URL.")
    slug = parts[0]
    return {"slug": slug}, f"https://apply.workable.com/{slug}"
