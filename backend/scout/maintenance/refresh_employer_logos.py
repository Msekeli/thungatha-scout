import argparse
import asyncio

from scout.branding.logo_discovery import (
    discover_employer_logo,
    is_usable_employer_logo_url,
)
from scout.maintenance.employer_logo_refresh_policy import (
    duplicate_employer_names,
    verified_website_for,
)
from scout.persistence.database_connection import get_database_connection


async def refresh_employer_logos(apply: bool = False) -> tuple[int, int]:
    with get_database_connection() as connection:
        employers = connection.execute(
            """
            SELECT e.id, e.name, e.website_url, e.logo_url, e.logo_type,
                   (
                       SELECT es.employer_careers_url
                       FROM employer_sources es
                       WHERE es.employer_id = e.id
                         AND es.employer_careers_url IS NOT NULL
                       ORDER BY es.created_at DESC
                       LIMIT 1
                   ) AS careers_url
            FROM employers e
            ORDER BY e.name
            """
        ).fetchall()

    updated = 0
    unresolved = 0
    duplicate_names = duplicate_employer_names(employers)
    for name in sorted(duplicate_names):
        print(f"UNRESOLVED: duplicate employer records for {name}")

    for employer in employers:
        if employer["name"].strip().casefold() in duplicate_names:
            unresolved += 1
            continue
        if employer["logo_type"] in {
            "official_logo",
            "official_favicon",
        } and is_usable_employer_logo_url(employer["logo_url"]):
            continue

        website_url = verified_website_for(employer)
        result = await discover_employer_logo(employer["careers_url"], website_url)
        if result is None:
            unresolved += 1
            print(
                f"No official logo or website icon found: {employer['name']} ({employer['id']})"
            )
            continue

        logo_url, source_url, logo_type = result
        if not apply:
            updated += 1
            print(
                f"DRY RUN: would update {employer['name']} with {logo_type} from {source_url}"
            )
            continue

        with get_database_connection() as connection, connection.transaction():
            saved = connection.execute(
                """
                UPDATE employers
                SET logo_url = %s, logo_source_url = %s, logo_type = %s, updated_at = NOW()
                WHERE id = %s
                  AND (
                      logo_type = 'unverified'
                      OR logo_url IS NULL
                      OR logo_url !~* '^https?://'
                      OR logo_url ILIKE 'https://www.google.com/s2/favicons%%'
                      OR logo_url ILIKE 'https://favicons.githubusercontent.com%%'
                      OR lower(logo_url) LIKE '%%greenhouse.io%%'
                      OR lower(logo_url) LIKE '%%lever.co%%'
                      OR lower(logo_url) LIKE '%%teamtailor.com%%'
                  )
                RETURNING id
                """,
                (logo_url, source_url, logo_type, employer["id"]),
            ).fetchone()
        if saved:
            updated += 1
            print(f"Updated logo: {employer['name']} ({employer['id']})")

    return updated, unresolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Refresh employer branding from official websites."
    )
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Persist discovered branding. Without this flag, only show proposed updates.",
    )
    arguments = parser.parse_args()
    updated, unresolved = asyncio.run(refresh_employer_logos(apply=arguments.apply))
    mode = "Applied" if arguments.apply else "Dry run"
    print(f"{mode}. Updated: {updated}; unresolved: {unresolved}.")
