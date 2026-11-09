from scout.geography import is_south_african_location


def test_accepts_south_african_location_text() -> None:
    assert is_south_african_location("Cape Town, Western Cape, South Africa")


def test_accepts_south_african_country_codes() -> None:
    assert is_south_african_location("ZA")
    assert is_south_african_location("ZAF")
    assert is_south_african_location("Remote, ZA")


def test_rejects_unknown_and_remote_only_locations() -> None:
    assert not is_south_african_location(None)
    assert not is_south_african_location("Remote")
    assert not is_south_african_location("London, United Kingdom")
