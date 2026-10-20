"""Thungatha Scout CLI entry point."""
from app.discovery import discover_companies


def main() -> None:
    print("Thungatha Scout — company discovery prototype")
    print("Scope: direct employers in Cape Town / Western Cape")
    print("No discovery provider is configured yet.")
    print("Known-URL verification is separate from discovering unknown companies.")
    print(f"Discovery candidates returned: {len(discover_companies())}")


if __name__ == "__main__":
    main()
