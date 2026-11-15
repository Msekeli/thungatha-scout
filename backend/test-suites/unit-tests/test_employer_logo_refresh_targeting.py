from scout.maintenance.employer_logo_refresh_targeting import (
    needs_targeted_logo_refresh,
)


def test_targeted_refresh_selects_missing_and_ats_logos_only() -> None:
    assert needs_targeted_logo_refresh({"logo_url": None, "logo_type": None})
    assert needs_targeted_logo_refresh({
        "logo_url": "https://cdn.example.com/logo.png",
        "logo_type": "official_ats_logo",
    })
    assert needs_targeted_logo_refresh({
        "logo_url": "https://cdn.example.com/logo.png",
        "logo_type": "official_logo",
        "logo_source_url": "https://jobs.lever.co/acme",
    })
    assert not needs_targeted_logo_refresh({
        "logo_url": "https://cdn.example.com/logo.png",
        "logo_type": "official_logo",
        "logo_source_url": "https://acme.com/careers",
    })
