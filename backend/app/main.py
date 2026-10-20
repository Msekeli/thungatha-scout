
from urllib.parse import urljoin, urlparse

import httpx
from bs4 import BeautifulSoup

CAREERS_URL = "https://careers.capitecbank.co.za/"

CAREER_KEYWORDS = (
    "career",
    "careers",
    "job",
    "jobs",
    "vacancy",
    "vacancies",
    "recruitment",
    "opportunities",
)


def inspect_careers_page(url: str) -> None:
    print(f"\nInspecting: {url}")
    print("-" * 60)

    try:
        with httpx.Client(
            follow_redirects=True,
            timeout=20.0,
            headers={
                "User-Agent": "ThungathaScout/0.1 (company verification prototype)"
            },
        ) as client:
            response = client.get(url)
            print(f"HTTP status: {response.status_code}")
            print(f"Final URL: {response.url}")
            print(f"Website reachable: {response.is_success}")

            response.raise_for_status()

    except httpx.HTTPError as exc:
        print(f"Request failed: {exc}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    title = soup.title.get_text(" ", strip=True) if soup.title else "Not found"
    description_tag = soup.find("meta", attrs={"name": "description"})
    description = (
        description_tag.get("content", "").strip()
        if description_tag
        else "Not found"
    )

    print(f"Page title: {title}")
    print(f"Meta description: {description or 'Not found'}")

    links = []
    for anchor in soup.find_all("a", href=True):
        href = urljoin(str(response.url), anchor["href"])
        text = anchor.get_text(" ", strip=True)
        parsed = urlparse(href)

        if parsed.scheme in ("http", "https"):
            searchable = f"{text} {parsed.path}".lower()
            if any(keyword in searchable for keyword in CAREER_KEYWORDS):
                links.append((text or "(no link text)", href))

    print("\nPotential careers/job links:")
    if links:
        for text, href in list(dict.fromkeys(links))[:20]:
            print(f"- {text}: {href}")
    else:
        print("- No matching links found in the returned HTML.")

    page_text = soup.get_text(" ", strip=True).lower()
    url_text = str(response.url).lower()
    title_text = title.lower()

    signals = [
        any(word in url_text for word in CAREER_KEYWORDS),
        any(word in title_text for word in CAREER_KEYWORDS),
        any(word in page_text for word in ("current vacancies", "search jobs")),
    ]

    print(f"\nCareers-page signals: {sum(signals)}/{len(signals)}")

    if sum(signals) >= 2:
        print("Preliminary classification: Likely careers page")
    elif sum(signals) == 1:
        print("Preliminary classification: Possible careers page")
    else:
        print("Preliminary classification: Uncertain")

    print("Note: This is a preliminary rule-based result, not verification.")


if __name__ == "__main__":
    inspect_careers_page(CAREERS_URL)
