"""Evidence-oriented inspection for known career URLs."""
from urllib.parse import urljoin, urlparse
import httpx
from bs4 import BeautifulSoup

CAREER_KEYWORDS = ("career", "careers", "job", "jobs", "vacancy", "vacancies", "recruitment", "opportunities", "work-for-us")
APPLICATION_HOST_HINTS = ("greenhouse.io", "lever.co", "myworkdayjobs.com", "successfactors", "smartrecruiters.com", "workable.com", "ashbyhq.com", "teamtailor.com", "jobs.personio.com")


def inspect_careers_page(url: str, *, timeout: float = 20.0) -> dict[str, object]:
    """Inspect a URL. Does not discover employers or prove hiring activity."""
    result: dict[str, object] = {"supplied_url": url, "http_status": "", "final_url": "", "reachable": False, "page_title": "", "meta_description": "", "headings": [], "careers_links": [], "application_links": [], "classification": "needs_review", "evidence": [], "error": ""}
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout, headers={"User-Agent": "Mozilla/5.0 (compatible; ThungathaScout/0.1; +https://github.com/Msekeli/thungatha-scout)"}) as client:
            response = client.get(url)
            result["http_status"] = response.status_code
            result["final_url"] = str(response.url)
            result["reachable"] = response.is_success
            response.raise_for_status()
    except (httpx.HTTPError, ValueError) as exc:
        result["error"] = str(exc)
        return result
    content_type = response.headers.get("content-type", "").lower()
    if "html" not in content_type and "xhtml" not in content_type:
        result["error"] = f"Response is not HTML (content-type: {content_type or 'unknown'})"
        return result
    soup = BeautifulSoup(response.text, "html.parser")
    title_tag = soup.find("title")
    title = title_tag.get_text(" ", strip=True) if title_tag else ""
    result["page_title"] = title
    description = soup.find("meta", attrs={"name": "description"})
    result["meta_description"] = description.get("content", "").strip() if description else ""
    headings = []
    for heading in soup.find_all(["h1", "h2", "h3"]):
        text = heading.get_text(" ", strip=True)
        if text and text not in headings:
            headings.append(text)
    result["headings"] = headings[:30]
    career_links, application_links, seen_careers, seen_apps = [], [], set(), set()
    for anchor in soup.find_all("a", href=True):
        href = urljoin(str(response.url), str(anchor["href"]).strip())
        parsed = urlparse(href)
        if parsed.scheme not in ("http", "https"):
            continue
        label = anchor.get_text(" ", strip=True) or "(no link text)"
        searchable = f"{label} {parsed.path} {parsed.netloc}".lower()
        item = {"label": label, "url": href}
        if any(k in searchable for k in CAREER_KEYWORDS) and href not in seen_careers:
            career_links.append(item); seen_careers.add(href)
        if any(h in parsed.netloc.lower() for h in APPLICATION_HOST_HINTS) and href not in seen_apps:
            application_links.append(item); seen_apps.add(href)
    result["careers_links"] = career_links[:50]
    result["application_links"] = application_links[:50]
    final_url = str(response.url).lower()
    signals = [any(k in final_url for k in CAREER_KEYWORDS), any(k in title.lower() for k in CAREER_KEYWORDS), any(k in " ".join(headings).lower() for k in CAREER_KEYWORDS)]
    evidence = []
    if signals[0]: evidence.append("Final URL contains a careers/job-related term.")
    if signals[1]: evidence.append("Page title contains a careers/job-related term.")
    if signals[2]: evidence.append("Page headings contain a careers/job-related term.")
    if career_links: evidence.append(f"Found {len(career_links)} careers/job-related links.")
    if application_links: evidence.append(f"Found {len(application_links)} links to recognised ATS host patterns.")
    result["evidence"] = evidence
    if sum(signals) >= 2 or (sum(signals) >= 1 and career_links):
        result["classification"] = "likely_careers_page"
    return result
