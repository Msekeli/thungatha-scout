from scout.geography import is_south_african_vacancy


def test_accepts_south_african_city():
    assert is_south_african_vacancy({"location": {"name": "Cape Town"}})


def test_accepts_explicit_south_africa_remote():
    assert is_south_african_vacancy({"location": {"name": "Remote - South Africa"}})


def test_accepts_south_african_office_evidence():
    assert is_south_african_vacancy({
        "location": {"name": "Hybrid"},
        "offices": [{"name": "Johannesburg, Gauteng"}],
    })


def test_rejects_remote_without_country_eligibility():
    assert not is_south_african_vacancy({"location": {"name": "Remote"}})


def test_rejects_non_south_african_location():
    assert not is_south_african_vacancy({"location": {"name": "London, UK"}})


def test_rejects_missing_location():
    assert not is_south_african_vacancy({})
