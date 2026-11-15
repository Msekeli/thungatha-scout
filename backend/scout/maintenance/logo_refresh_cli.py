import argparse
import asyncio


def run_cli(refresh_employer_logos):
    parser = argparse.ArgumentParser(description="Refresh employer branding safely.")
    parser.add_argument("--apply", action="store_true", help="Persist replacements.")
    parser.add_argument("--recheck-existing", action="store_true", help="Recheck reachable logos.")
    parser.add_argument(
        "--only-needs-refresh",
        action="store_true",
        help="Refresh only missing logos and logos sourced from ATS platforms.",
    )
    args = parser.parse_args()
    updated, unresolved = asyncio.run(
        refresh_employer_logos(
            apply=args.apply,
            recheck_existing=args.recheck_existing,
            only_needs_refresh=args.only_needs_refresh,
        )
    )
    mode = "Applied" if args.apply else "Dry run"
    print(f"{mode}. Updated: {updated}; unresolved: {unresolved}.")
