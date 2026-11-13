import argparse
import asyncio

from scout.employer_branding.logo_discovery import discover_employer_logo
from scout.employer_branding.logo_http import inspect_existing_logo
from scout.maintenance.employer_careers_validation import careers_page_matches_employer
from scout.maintenance.employer_logo_refresh_policy import (
    duplicate_employer_names,
    verified_website_for,
)
from scout.maintenance.employer_logo_refresh_persistence import (\n    load_employers,\n    persist_logo,\n)


async def refresh_employer_logos(
    apply: bool = False, recheck_existing: bool = False
) -> tuple[int, int]:
    employers = load_employers()
    updated = unresolved = 0
    duplicates = duplicate_employer_names(employers)
    for name in sorted(duplicates):
        print(f"DUPLICATE_REQUIRES_REVIEW: {name}")
    for employer in employers:
        name = employer["name"]
        if name.strip().casefold() in duplicates:
            unresolved += 1
            continue
        status = await inspect_existing_logo(employer["logo_url"])
        if status in {"valid", "unknown"} and not recheck_existing:
            print(f"EXISTING_LOGO_RETAINED: {name} ({status})")
            continue
        website_url = verified_website_for(employer)
        source_urls = employer["source_urls"] or []
        careers_url = employer["careers_url"]
        if careers_url and not careers_page_matches_employer(
            name, careers_url, website_url
        ):
            print(f"UNVERIFIED_CAREERS_URL: {name} {careers_url}")
            careers_url = None
        if not website_url and not source_urls and not careers_url:
            unresolved += 1
            print(f"NO_VERIFIED_DISCOVERY_SOURCE: {name} ({employer['id']})")
            continue
        diagnostics: list[str] = []
        result = await discover_employer_logo(
            careers_url,
            website_url,
            employer_name=name,
            source_urls=source_urls,
            diagnostics=diagnostics,
        )
        if result is None:
            unresolved += 1
            reason = ",".join(dict.fromkeys(diagnostics)) or "NO_CANDIDATE"
            outcome = (
                "NO_REPLACEMENT_FOUND" if employer["logo_url"] else "NO_LOGO_FOUND"
            )
            print(f"{outcome}: {name} ({employer['id']}) reason={reason}")
            continue
        logo_url, source_url, logo_type = result
        print(
            f"CANDIDATE_DISCOVERED: {name} {logo_type} "
            f"source={source_url} image={logo_url}"
        )
        if not apply:
            updated += 1
            continue
        saved = persist_logo(employer, logo_url, source_url, logo_type)
        if saved:
            updated += 1
            print(f"UPDATED: {name} ({employer['id']})")
        else:
            print(f"RETAINED_CONCURRENT_CHANGE: {name} ({employer['id']})")
    return updated, unresolved


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Refresh employer branding safely.")
    parser.add_argument("--apply", action="store_true", help="Persist replacements.")
    parser.add_argument(
        "--recheck-existing",
        action="store_true",
        help="Discover replacements even when an existing image is reachable.",
    )
    args = parser.parse_args()
    updated, unresolved = asyncio.run(
        refresh_employer_logos(apply=args.apply, recheck_existing=args.recheck_existing)
    )
    mode = "Applied" if args.apply else "Dry run"
    print(f"{mode}. Updated: {updated}; unresolved: {unresolved}.")
