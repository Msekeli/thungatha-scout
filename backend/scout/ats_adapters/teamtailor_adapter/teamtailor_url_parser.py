from urllib.parse import urlsplit, urlunsplit


def parse_teamtailor_careers_url(source_url: str) -> tuple[dict[str, str], str]:
    if not isinstance(source_url, str) or not source_url.strip():
        raise ValueError("Teamtailor configuration requires a careers URL.")
    try:
        parsed = urlsplit(source_url.strip())
        valid = (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and parsed.port is None
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and parsed.path.rstrip("/").endswith("/jobs")
        )
    except ValueError as exception:
        raise ValueError("Teamtailor careers URL is invalid.") from exception
    if not valid:
        raise ValueError("Use an HTTPS Teamtailor careers URL ending in /jobs.")
    path = parsed.path.rstrip("/")
    careers_url = urlunsplit(("https", parsed.netloc, path, "", ""))
    feed_url = urlunsplit(("https", parsed.netloc, path + ".rss", "", ""))
    return {"careers_url": careers_url}, feed_url
