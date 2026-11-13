from collections import Counter
import re
from typing import Any
from urllib.parse import urlparse


VERIFIED_EMPLOYER_WEBSITES = {
    "aleph": "https://getaleph.com/",
    "aston holmes": "https://www.astonholmes.com/",
    "bamboo": "https://investbamboo.co.za/",
    "brafton": "https://www.brafton.com/",
    "cyberone": "https://cyberonesecurity.co.za/",
    "ekco": "https://www.ek.co/",
    "footasylum": "https://www.footasylum.com/",
    "impact.com": "https://impact.com/",
    "lyrahealth": "https://www.lyrahealth.com/",
    "moburst": "https://www.moburst.com/",
    "network recruitment": "https://www.networkrecruitment.co.za/",
    "paystack": "https://paystack.com/",
    "pick n pay": "https://www.pnp.co.za/",
    "sedna": "https://sedna.com/",
    "takealot group": "https://www.takealot.com/",
    "teamviewer": "https://www.teamviewer.com/",
    "theodo": "https://www.theodo.com/",
    "yassir": "https://yassir.com/",
    "2u": "https://2u.com/",
    "acacium group": "https://acaciumgroup.com/",
    "anew hotels & resorts": "https://anewhotels.com/",
    "biovac": "https://biovac.co.za/",
    "burnt studios": "https://burnt.co.za/",
    "bvnk": "https://www.bvnk.com/",
    "cosmo central group": "https://www.cosmocentralgroup.co.za/",
    "crosscountry consulting": "https://www.crosscountry-consulting.com/",
    "currenciesdirectlimited": "https://www.currenciesdirect.com/",
    "magentus": "https://www.magentus.com/",
    "moonpay": "https://www.moonpay.com/",
    "north star network": "https://north-star.network/",
    "old mutual": "https://www.oldmutual.com/",
    "olx": "https://www.olx.com/",
    "onedayonly": "https://www.onedayonly.co.za/",
    "ozow": "https://ozow.com/",
    "parallelwireless": "https://www.parallelwireless.com/",
    "payjoy": "https://www.payjoy.com/"
}


_ATS_SUFFIXES = (".greenhouse.io", ".lever.co", ".teamtailor.com")
_CAREERS_PATH_SEGMENTS = {"careers", "career", "jobs", "job"}


def _tokens(value: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", value.casefold()))


def _website_matches_employer(name: str, website: str) -> bool:
    host = (urlparse(website).hostname or "").casefold().removeprefix("www.")
    host_tokens = _tokens(host)
    employer_tokens = {token for token in _tokens(name) if len(token) >= 3}
    if not host_tokens or not employer_tokens:
        return False
    host_compact = "".join(host_tokens)
    name_compact = "".join(employer_tokens)
    return bool(host_tokens.intersection(employer_tokens)) or (
        len(name_compact) >= 5 and name_compact in host_compact
    )


def verified_website_for(employer: dict[str, Any]) -> str | None:
    name = employer["name"].strip().casefold()
    mapped = VERIFIED_EMPLOYER_WEBSITES.get(name)
    if mapped:
        return mapped
    website = employer.get("website_url")
    if not website or not _website_matches_employer(name, str(website)):
        return None
    parsed = urlparse(str(website))
    host = (parsed.hostname or "").casefold()
    if host in {"greenhouse.io", "lever.co", "teamtailor.com"} or host.endswith(
        _ATS_SUFFIXES
    ):
        return None
    if any(
        segment.casefold() in _CAREERS_PATH_SEGMENTS
        for segment in parsed.path.split("/")
    ):
        return None
    return str(website)


def duplicate_employer_names(employers: list[dict[str, Any]]) -> set[str]:
    names = [employer["name"].strip().casefold() for employer in employers]
    return {name for name, count in Counter(names).items() if count > 1}
