import argparse
import asyncio

from scout.branding.logo_discovery import discover_employer_logo
from scout.branding.logo_http import inspect_existing_logo
from scout.maintenance.employer_logo_refresh_policy import (
    duplicate_employer_names,
    verified_website_for,
)
from scout.persistence.database_connection import get_database_connection


async def refresh_employer_logos(apply: bool = False) -> tuple[int, int]:
    with get_database_connection() as connection:
        employers = connection.execute(
            """SELECT e.id, e.name, e.website_url, e.logo_url,
                      (SELECT es.employer_careers_url FROM employer_sources es
                       WHERE es.employer_id = e.id AND es.employer_careers_url IS NOT NULL
                       ORDER BY es.created_at DESC LIMIT 1) AS careers_url
               FROM employers e ORDER BY e.name"""
        ).fetchall()
    updated = unresolved = 0
    duplicates = duplicate_employer_names(employers)
    for name in sorted(duplicates):
        print(f"DUPLICATE_REQUIRES_REVIEW: {name}")
    for employer in employers:
        if employer["name"].strip().casefold() in duplicates:
            unresolved += 1
            continue
        status = await inspect_existing_logo(employer["logo_url"])
        if status in {"valid", "unknown"}:
            print(f"EXISTING_LOGO_RETAINED: {employer['name']} ({status})")
            continue
        rejected = []
        result = await discover_employer_logo(
            employer["careers_url"], verified_website_for(employer), rejected
        )
        if result is None:
            unresolved += 1
            outcome = "CANDIDATE_REJECTED" if rejected else "NO_LOGO_FOUND"
            print(f"{outcome}: {employer['name']} ({employer['id']})")
            continue
        logo_url, source_url, logo_type = result
        print(f"CANDIDATE_DISCOVERED: {employer['name']} {logo_type} {logo_url}")
        if not apply:
            updated += 1
            continue
        with get_database_connection() as connection, connection.transaction():
            saved = connection.execute(
                """UPDATE employers
                   SET logo_url = %s, logo_source_url = %s, logo_type = %s,
                       updated_at = NOW()
                   WHERE id = %s AND logo_url IS NOT DISTINCT FROM %s
                   RETURNING id""",
                (logo_url, source_url, logo_type, employer["id"], employer["logo_url"]),
            ).fetchone()
        if saved:
            updated += 1
            print(f"UPDATED: {employer['name']} ({employer['id']})")
        else:
            print(f"RETAINED_CONCURRENT_CHANGE: {employer['name']} ({employer['id']})")
    return updated, unresolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh employer branding safely.")
    parser.add_argument("--apply", action="store_true", help="Persist safe replacements.")
    args = parser.parse_args()
    updated, unresolved = asyncio.run(refresh_employer_logos(apply=args.apply))
    print(f"{'Applied' if args.apply else 'Dry run'}. Updated: {updated}; unresolved: {unresolved}.")
