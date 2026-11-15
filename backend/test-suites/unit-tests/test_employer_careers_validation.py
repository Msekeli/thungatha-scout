from scout.maintenance.employer_careers_validation import careers_page_matches_employer


def test_accepts_careers_subdomain_of_verified_employer_domain() -> None:
    assert careers_page_matches_employer(
        "ANEW Hotels & Resorts",
        "https://careers.anewhotels.com/jobs",
        "https://anewhotels.com/",
    )


def test_accepts_workable_board_slug() -> None:
    assert careers_page_matches_employer(
        "DigiOutsource", "https://apply.workable.com/digioutsource/"
    )
