from urllib.parse import urlparse


def match_existing_source(sources: list[dict], pages: tuple) -> dict | None:
    for page in pages:
        page_url = urlparse(page.final_url)
        page_path = page_url.path.rstrip("/")
        for source in sources:
            if source["adapter_key"] == "career_page":
                continue
            source_url = urlparse(source["source_url"])
            source_path = source_url.path.rstrip("/")
            same_url = (
                page_url.scheme == source_url.scheme
                and page_url.netloc == source_url.netloc
                and page_path == source_path
            )
            same_ats = (
                page.platform_key == source["adapter_key"]
                and page_url.hostname == source_url.hostname
                and (
                    page_path == source_path or page_path.startswith(source_path + "/")
                )
            )
            if same_url or same_ats:
                return source
    return None
