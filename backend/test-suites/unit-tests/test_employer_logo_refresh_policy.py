from scout.maintenance.employer_logo_refresh_policy import (
    duplicate_employer_names,
    verified_website_for,
)


def employer(name: str, website_url: str | None = None) -> dict[str, str | None]:
    return {"name": name, "website_url": website_url}


def test_verified_mapping_overrides_careers_page() -> None:
    assert (
        verified_website_for(employer("Impact.com", "https://impact.com/careers/"))
        == "https://impact.com/"
    )
    assert (
        verified_website_for(employer("Pick n Pay", "https://www.pnp.co.za/careers"))
        == "https://www.pnp.co.za/"
    )
    assert (
        verified_website_for(
            employer("TeamViewer", "https://careers.teamviewer.com/jobs")
        )
        == "https://www.teamviewer.com/"
    )


def test_unmapped_careers_page_is_not_an_official_website() -> None:
    assert (
        verified_website_for(employer("Unknown", "https://example.com/careers")) is None
    )


def test_verified_questionable_mappings_are_preserved() -> None:
    assert verified_website_for(employer("Bamboo")) == "https://investbamboo.co.za/"
    assert verified_website_for(employer("OLX")) == "https://www.olx.com/"
    assert (
        verified_website_for(employer("North Star Network"))
        == "https://north-star.network/"
    )


def test_duplicate_names_are_reported_once() -> None:
    records = [
        employer("Biovac"),
        employer("Biovac"),
        employer("OneDayOnly"),
        employer("OneDayOnly"),
        employer("Unique"),
    ]
    assert duplicate_employer_names(records) == {"biovac", "onedayonly"}


def test_rejects_parent_company_domain_for_different_employer() -> None:
    assert verified_website_for(
        employer("Digioutsource", "https://supergroup.com/")
    ) is None


def test_accepts_domain_matching_employer_name() -> None:
    assert verified_website_for(
        employer("Astron Energy", "https://www.astronenergy.co.za/")
    ) == "https://www.astronenergy.co.za/"


def test_rejects_generic_ats_domain_as_employer_website() -> None:
    assert verified_website_for(
        employer("Example Company", "https://boards.greenhouse.io/example")
    ) is None
