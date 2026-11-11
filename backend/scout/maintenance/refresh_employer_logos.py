import asyncio

from scout.branding.logo_discovery import (
    discover_employer_logo,
    is_usable_employer_logo_url,
)
from scout.persistence.database_connection import get_database_connection


# Official company websites verified for employers whose website_url is missing.
# Ambiguous employer names are intentionally excluded.
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
    "payjoy": "https://www.payjoy.com/",
}


async def refresh_employer_logos() -> tuple[int, int]:
    with get_database_connection() as connection:
        employers = connection.execute(
            """
            SELECT e.id, e.name, e.website_url, e.logo_url,
                   (
                       SELECT s.employer_careers_url
                       FROM employer_sources s
                       WHERE s.employer_id = e.id
                       ORDER BY s.created_at
                       LIMIT 1
                   ) AS careers_url
            FROM employers e
            ORDER BY e.name
            """
        ).fetchall()

    updated = 0
    unresolved = 0
    for employer in employers:
        if is_usable_employer_logo_url(employer["logo_url"]):
            continue

        website_url = employer["website_url"]
        if website_url:
            from urllib.parse import urlparse

            hostname = (urlparse(website_url).hostname or "").casefold()
            if (
                hostname == "greenhouse.io"
                or hostname.endswith(".greenhouse.io")
                or hostname == "lever.co"
                or hostname.endswith(".lever.co")
                or hostname == "teamtailor.com"
                or hostname.endswith(".teamtailor.com")
            ):
                website_url = None

        website_url = website_url or VERIFIED_EMPLOYER_WEBSITES.get(
            employer["name"].strip().casefold()
        )
        result = await discover_employer_logo(employer["careers_url"], website_url)
        if result is None:
            unresolved += 1
            print(
                f"No official logo or website icon found: {employer['name']} ({employer['id']})"
            )
            continue

        logo_url, source_url = result
        with get_database_connection() as connection, connection.transaction():
            saved = connection.execute(
                """
                UPDATE employers
                SET logo_url = %s, logo_source_url = %s, updated_at = NOW()
                WHERE id = %s
                  AND (
                      logo_url IS NULL
                      OR logo_url !~* '^https?://'
                      OR logo_url ILIKE 'https://www.google.com/s2/favicons%%'
                      OR logo_url ILIKE 'https://favicons.githubusercontent.com%%'
                      OR lower(logo_url) LIKE '%%greenhouse.io%%'
                      OR lower(logo_url) LIKE '%%lever.co%%'
                      OR lower(logo_url) LIKE '%%teamtailor.com%%'
                  )
                RETURNING id
                """,
                (logo_url, source_url, employer["id"]),
            ).fetchone()
        if saved:
            updated += 1
            print(f"Updated logo: {employer['name']} ({employer['id']})")

    return updated, unresolved


if __name__ == "__main__":
    updated, unresolved = asyncio.run(refresh_employer_logos())
    print(f"Logo discovery complete. Updated: {updated}; unresolved: {unresolved}.")
