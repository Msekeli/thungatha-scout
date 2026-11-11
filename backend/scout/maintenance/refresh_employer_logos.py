import asyncio

from scout.branding.logo_discovery import (
    discover_employer_logo,
    is_usable_employer_logo_url,
)
from scout.persistence.database_connection import get_database_connection


async def refresh_employer_logos() -> tuple[int, int]:
    with get_database_connection() as connection:
        employers = connection.execute(
            """
            SELECT e.id, e.website_url, e.logo_url,
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
        result = await discover_employer_logo(
            employer["careers_url"], employer["website_url"]
        )
        if result is None:
            unresolved += 1
            print(f"No official logo or website icon found: {employer['id']}")
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
                      OR logo_url ILIKE 'https://www.google.com/s2/favicons%'
                      OR logo_url ILIKE 'https://favicons.githubusercontent.com%'
                      OR lower(logo_url) LIKE '%greenhouse.io%'
                      OR lower(logo_url) LIKE '%lever.co%'
                      OR lower(logo_url) LIKE '%teamtailor.com%'
                  )
                RETURNING id
                """,
                (logo_url, source_url, employer["id"]),
            ).fetchone()
        if saved:
            updated += 1
            print(f"Updated logo: {employer['id']}")
    return updated, unresolved


if __name__ == "__main__":
    updated, unresolved = asyncio.run(refresh_employer_logos())
    print(f"Logo discovery complete. Updated: {updated}; unresolved: {unresolved}.")
